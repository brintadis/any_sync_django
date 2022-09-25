import os
import shutil
import requests
from PIL import Image
from random import shuffle

from django.conf import settings


class CollageMaker:
    """
    Make a collage of the image using 4< other images
    """
    def __init__(self, user) -> None:
        self.user = user
        self.media_root = settings.MEDIA_ROOT
        self.media_url = settings.MEDIA_URL

    def make_collage(self, images, filename, width=200, init_height=100):
        """
        Make a collage image with a width equal to `width`
        from `images` and save to `filename`.
        """
        if not images:
            print("No images for collage found!")
            return False

        margin_size = 2
        # run until a suitable arrangement of images is found
        while True:
            # copy images to images_list
            images_list = images[:]
            coefs_lines = []
            images_line = []
            x = 0
            while images_list:
                # get first image and resize to `init_height`
                img_path = images_list.pop(0)
                img = Image.open(img_path)
                img.thumbnail((width, init_height))
                # when `x` will go beyond the `width`, start the next line
                if x > width:
                    coefs_lines.append((float(x) / width, images_line))
                    images_line = []
                    x = 0
                x += img.size[0] + margin_size
                images_line.append(img_path)
            # finally add the last line with images
            coefs_lines.append((float(x) / width, images_line))

            # compact the lines, by reducing the `init_height`,
            # if any with one or less images
            if len(coefs_lines) <= 1:
                break
            if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
                # reduce `init_height`
                init_height -= 10
            else:
                break

        # get output height
        out_height = 0
        for coef, imgs_line in coefs_lines:
            if imgs_line:
                out_height += int(init_height / coef) + margin_size
        if not out_height:
            print("Height of collage could not be 0!")
            return False

        collage_image = Image.new("RGB", (width, int(out_height)), (35, 35, 35))
        # put images to the collage
        y = 0
        for coef, imgs_line in coefs_lines:
            if imgs_line:
                x = 0
                for img_path in imgs_line:
                    img = Image.open(img_path)
                    # if need to enlarge an image - use `resize`,
                    # otherwise use `thumbnail`, it's faster
                    k = (init_height / coef) / img.size[1]
                    if k > 1:
                        img = img.resize(
                            (int(img.size[0] * k), int(img.size[1] * k)), Image.ANTIALIAS
                        )
                    else:
                        img.thumbnail(
                            (int(width / coef), int(init_height / coef)), Image.ANTIALIAS
                        )
                    if collage_image:
                        collage_image.paste(img, (int(x), int(y)))
                    x += img.size[0] + margin_size
                y += int(init_height / coef) + margin_size
        collage_image.save(filename)

    def get_collage_items(self, list_image_urls):
        """Parse an image list with url equal to `url` and save it.

        Args:
            list_image_urls (_list_): Img urls

        Returns:
            _list_: Return a `list` of img paths.
        """
        name_num = 1
        img_path_list = []
        os.makedirs(self.media_root + f"images/yandex_collage_temp/{self.user.id}/", exist_ok=True)
        for img in list_image_urls:
            resp = requests.get(img, stream=True).raw
            img = Image.open(resp, mode="r")
            path_to_save = self.media_root + f"images/yandex_collage_temp/{self.user.id}/\
                pict{name_num}.png"
            img.save(path_to_save, "png")
            img_path_list.append(path_to_save)
            name_num += 1
        return img_path_list

    def cover_processing(self, playlist, username, kind_playlist):
        """This function processes the cover url and makes a collage.

        Args:
            playlist: playlist obj from Yandex.
            username (`str`): Username.
            kind_playlist (`str`): Yandex playlist id.

        Returns:
            `str`: return collage url.
        """
        list_image_urls = []
        for cover in playlist.cover.items_uri:
            img_cover_url = cover.replace("%%", "200x200")
            img_cover_url = f"https://{img_cover_url}"
            list_image_urls.append(img_cover_url)

        if len(list_image_urls) == 1:
            img_cover_url = list_image_urls[0]

        elif len(list_image_urls) == 2:
            list_image_urls += list_image_urls
            shuffle(list_image_urls)

        elif len(list_image_urls) == 3:
            list_image_urls.append(list_image_urls[0])

        img_name = f"{username}_{kind_playlist}.png"
        collage_image_path = self.media_root + f"images/yandex_playlist_collages/{img_name}"
        os.makedirs(self.media_root + "images/yandex_playlist_collages/")
        if len(list_image_urls) != 1:
            self.make_collage(
                images=self.get_collage_items(list_image_urls),
                filename=collage_image_path,
            )
            img_cover_url = self.media_url + f"images/yandex_playlist_collages/{img_name}"

        # Remove temp dir with temp imgs.
        if os.path.isdir(self.media_root + "images/yandex_collage_temp"):
            shutil.rmtree(self.media_root + f"images/yandex_collage_temp/{self.user.id}")

        return img_cover_url
