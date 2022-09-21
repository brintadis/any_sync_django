import json
from datetime import datetime, timedelta
from time import sleep

from yandex_music import Client

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common.by import By

from ya_music.collage_maker import CollageMaker
from playlist.models import Playlist, Track


class ImportYandexMusicPlaylistByUrl:
    def __init__(self, playlist_url, user) -> None:
        self.playlist_url = playlist_url
        self.user = user

    def get_yandex_playlist_by_url(self):
        username = self.playlist_url.split("/")[4]
        kind_playlist = self.playlist_url.split("/")[-1]
        playlist = Client().users_playlists(int(kind_playlist), username)
        playlist_name = playlist.title
        owner_name = playlist.owner["name"]
        tracks = playlist.tracks

        if playlist.cover["uri"] is None:
            collage_maker = CollageMaker(self.user)
            img_cover_url = collage_maker.cover_processing(
                playlist=playlist, username=username, kind_playlist=kind_playlist
            )
        else:
            img_cover_url = str(playlist.cover["uri"]).replace("%%", "200x200")
            img_cover_url = f"https://{img_cover_url}"

        self.save_playlist_into_db(
            playlist_name=playlist_name,
            owner_name=owner_name,
            img_cover=img_cover_url,
            tracks=tracks,
        )

    def save_playlist_into_db(self, playlist_name, owner_name, tracks, img_cover):
        """Save playlist and tracks into db"""
        print(img_cover)
        new_playlist = Playlist(
            user=self.user,
            playlist_name=playlist_name,
            owner_name=owner_name,
            img_cover_url=img_cover,
        )
        new_playlist.save()

        track_list = []

        for track in tracks:
            duration_ms = int(track["track"]["duration_ms"])
            duration_and_random_date = datetime(1970, 1, 1) + timedelta(
                milliseconds=duration_ms
            )
            duration = duration_and_random_date.strftime("%M:%S")

            img_cover_url = str(track["track"]["cover_uri"]).replace("%%", "200x200")
            img_cover_url = f"https://{img_cover_url}"

            new_track = Track(
                playlist=new_playlist,
                artist=track["track"]["artists"][0]["name"],
                track_name=track["track"]["title"],
                duration=duration,
                img_cover_url=img_cover_url,
            )
            track_list.append(new_track)

        Track.objects.bulk_create(track_list)


class YandexAuth:
    def __init__(self, email, password) -> None:
        self.email = email
        self.password = password

    def is_active(self, driver):
        """
        Check if selenium driver is active
        """
        try:
            driver.execute(Command.GET_ALL_COOKIES)
            return True
        except Exception:
            return False

    def close_webdriver(self, driver):
        """
        Close selenium webdriver
        """
        try:
            driver.close()
            driver.quit()
        except Exception:
            pass

    def get_token(self, driver):
        """
        Extracting token from logs, saving into db
        """

        token = None

        print(f"Token: {token}")

        while token is None and self.is_active(driver):
            sleep(1)
            try:
                logs_raw = driver.get_log("performance")
            except Exception:
                pass

            for lr in logs_raw:
                log = json.loads(lr["message"])["message"]
                url_fragment = log.get("params", {}).get("frame", {}).get("urlFragment")

                if url_fragment:
                    token = url_fragment.split("&")[0].split("=")[1]

        print(f"Token: {token}")

        # User.query.filter(User.id == current_user.id).update(dict(yandex_token=token))
        # db.session.commit()

        self.close_webdriver(driver)

        return token

    def yandex_auth(self):
        """
        Yandex auth using selenium webdriver
        """
        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"performance": "ALL"}
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Remote(
            desired_capabilities=capabilities,
            command_executor="http://selenium:4444/wd/hub",
            options=options,
            )
        driver.get(
            "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d"  # noqa: E501
        )

        sleep(2)
        print(f'Email: {self.email}, password: {self.password}')
        driver.find_element(By.ID, "passp-field-login").send_keys(self.email)
        driver.find_element(By.ID, "passp:sign-in").click()
        sleep(2)

        try:
            driver.find_element(By.CLASS_NAME, "CodeField")
            self.close_webdriver(driver)
            return False, 'Неправильная электронная почта'
        except NoSuchElementException:
            pass

        driver.find_element(By.ID, "passp-field-passwd").send_keys(self.password)
        driver.find_element(By.ID, "passp:sign-in").click()

        try:
            sleep(1)
            driver.find_element(By.ID, "field:input-passwd:hint")
            self.close_webdriver(driver)
            return False, 'Неверный пароль'
        except NoSuchElementException:
            pass

        token = self.get_token(driver)

        if token is None:
            return False, 'Ошибка при авторизации, пожалуйста, попробуйте еще раз'

        return token, "Вы успешно авторизовались через Яндекс"


def validate_token(token):
    try:
        Client(token).init()
        return True
    except Exception:
        return False


class SyncYandexPlaylists:
    """Create new playlist

    Args:
        token (`str`): unique yadnex auth key
        playlist_ids (`list`): playlist ids from our db to create
    """
    def __init__(self, token, playlist_ids, visibility) -> None:
        self.token = token
        self.playlist_ids = playlist_ids
        self.visibility = visibility
        self.client = Client(self.token).init()

    def sync_playlists(self):
        all_skipped_songs = []
        for playlist_id in self.playlist_ids:
            playlist_to_create = Playlist.objects.filter(id=playlist_id).first()
            new_playlist = self.client.users_playlists_create(playlist_to_create.playlist_name)
            tracks = Track.objects.filter(playlist=playlist_id).all()

            revision = 1
            skipped_songs = []
            for track in tracks:
                search_result = self.client.search(
                    f"{track.track_name} {track.artist}",
                    type_="all",
                )

                if search_result.best is None:
                    print(f"Трек {track} отсутствует")
                    skipped_songs.append(f"{track.track_name} by {track.artist}")
                else:
                    if search_result.best.type == "track":
                        track_id = search_result.best.result.id
                        album_id = search_result.best.result.albums[0].id

                        self.client.users_playlists_insert_track(
                            kind=new_playlist.kind,
                            track_id=track_id,
                            album_id=album_id,
                            revision=revision,
                        )
                        revision += 1
                    else:
                        print(f"Трек {track} отсутствует")
                        skipped_songs.append(f"{track.track_name} by {track.artist}")
            revision = 0
            if skipped_songs:
                all_skipped_songs.append({playlist_to_create.playlist_name: skipped_songs})
        return all_skipped_songs
