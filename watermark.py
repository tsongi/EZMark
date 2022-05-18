from PIL import ImageFont, ImageDraw, ImageFilter, Image

TEXT_PREVIEW_PATH = ".temporary/text_preview_img.png"
IMAGE_PREVIEW_PATH = ".temporary/image_preview_img.png"


class Watermarker:

    def watermark_preview(self, controller, operation: str, path: str, position: str, margin_x: int, margin_y: int, **kwargs):
        """Returns a preview of the current state of the watermarking process as an image"""
        base_img = Image.open(path)
        font_size = kwargs.get("font_size")
        text = kwargs.get("text")
        image_size = kwargs.get("image_size")
        watermark_path = kwargs.get("watermark_path")
        colour = kwargs.get("colour")

        if operation == "text":
            text_preview_img = self.place_text_watermark(image=base_img, font_size=font_size, text=text,
                                                         position=position, margin_x=margin_x,
                                                         margin_y=margin_y, colour=colour)
            text_preview_img = self._convert_to_preview_size(controller=controller, image=text_preview_img)
            text_preview_img.save(TEXT_PREVIEW_PATH)
        elif operation == "image":
            if watermark_path is not None:
                watermark_img = Image.open(watermark_path)
            else:
                watermark_img = None
            image_preview_img = self.place_image_watermark(base_img, watermark_img, size=image_size,
                                                           position=position, margin_x=margin_x, margin_y=margin_y)
            image_preview_img = self._convert_to_preview_size(controller=controller, image=image_preview_img)
            image_preview_img.save(IMAGE_PREVIEW_PATH)

    def place_text_watermark(self, image: Image, font_size: int, position: str, margin_x: int,
                             margin_y: int, colour: str, text) -> Image:
        """Adds text watermark to the base image"""
        if text is not None:
            title_font = ImageFont.truetype("helveticaneue.ttf", font_size)
            image_width, image_height = image.size
            text_width, text_height = self._get_text_dimensions(text, title_font)
            if position == "top-left":
                text_x = margin_x
                text_y = margin_y
            elif position == "top-right":
                text_x = image_width - text_width - margin_x
                text_y = margin_y
            elif position == "bottom-left":
                text_x = margin_x
                text_y = image_height - text_height - margin_y
            elif position == "bottom-right":
                text_x = image_width - text_width - margin_x
                text_y = image_height - text_height - margin_y
            else:
                raise ValueError
            image_editable = ImageDraw.Draw(image)
            image_editable.text((text_x, text_y), text, colour, font=title_font)
            return image
        else:
            return image

    def place_image_watermark(self, image, watermark_image, size: str,
                              position: str, margin_x: int, margin_y: int) -> Image:
        """Adds image watermark to the base image"""
        if watermark_image is not None:
            image_width, image_height = image.size
            watermark_image = self._resize_watermark(image_width, watermark_image, size=size)
            watermark_image_width, watermark_image_height = watermark_image.size
            image = image.copy()
            if position == "top-left":
                wm_x = margin_x
                wm_y = margin_y
            elif position == "top-right":
                wm_x = image_width - watermark_image_width - margin_x
                wm_y = margin_y
            elif position == "bottom-left":
                wm_x = margin_x
                wm_y = image_height - watermark_image_height - margin_y
            elif position == "bottom-right":
                wm_x = image_width - watermark_image_width - margin_x
                wm_y = image_height - watermark_image_height - margin_y
            else:
                raise ValueError
            image.paste(watermark_image, (wm_x, wm_y))
            return image
        else:
            return image

    def _resize_watermark(self, image_width, watermark_image, size):
        """Resizes the watermark image into the requested size."""
        watermark_image_width, watermark_image_height = watermark_image.size
        wm_ratio = watermark_image_height / watermark_image_width
        if size == "large":
            resized_wm_width = int(image_width * 0.15)
        elif size == "medium":
            resized_wm_width = int(image_width * 0.10)
        elif size == "small":
            resized_wm_width = int(image_width * 0.05)
        else:
            raise ValueError
        resized_wm_height = int(resized_wm_width * wm_ratio)
        new_size = (resized_wm_width, resized_wm_height)
        resized_wm = watermark_image.resize(new_size)
        return resized_wm

    def _get_text_dimensions(self, text_string: str, font):
        """Returns the dimensions of a string when rendered in pixels."""
        # https://stackoverflow.com/a/46220683/9263761
        ascent, descent = font.getmetrics()

        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return text_width, text_height

    def _convert_to_preview_size(self, image: Image, controller) -> Image:
        """Resizes the image to fit into the preview canvas on the GUI."""
        width, height = image.size
        ratio = width / height
        if ratio > 1:
            new_width = 500
            new_height = int(new_width * ratio)
        elif ratio < 1:
            new_height = 500
            new_width = int(new_height / ratio)
        else:
            new_width = 500
            new_height = 500
        new_size = (new_width, new_height)
        controller.preview_width, controller.preview_height = new_size
        preview_size_image = image.resize(new_size, Image.ANTIALIAS)
        return preview_size_image
