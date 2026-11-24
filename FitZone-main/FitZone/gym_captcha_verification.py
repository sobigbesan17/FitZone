import io
import random
import string
from PIL import Image, ImageDraw, ImageFont

try:
    from captcha.image import ImageCaptcha
except ImportError:
    ImageCaptcha = None


class CaptchaVerification:
    def __init__(self, length=6):
        self.length = length
        self.captcha_text = ""

    def generate_captcha(self):
        characters = string.ascii_letters + string.digits
        self.captcha_text = "".join(random.choices(characters, k=self.length))
        return self.captcha_text

    def get_captcha_image(self):
        if not self.captcha_text:
            self.generate_captcha()
        return self._create_image(self.captcha_text)

    def refresh_captcha_image(self):
        self.generate_captcha()
        return self._create_image(self.captcha_text)

    def _create_image(self, text):
        if ImageCaptcha is not None:
            try:
                image_captcha = ImageCaptcha(width=280, height=90)
                data = image_captcha.generate(text)
                return Image.open(data)
            except Exception:
                pass

        width, height = 280, 90
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            font = ImageFont.load_default()

        text_width, text_height = draw.textsize(text, font=font)
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))

        for _ in range(3):
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            draw.line([start, end], fill=(random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)), width=2)

        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            draw.point((x, y), fill=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

        return image

    def verify_captcha(self, user_input):
        return user_input.strip() == self.captcha_text

    def get_captcha_text(self):
        return self.captcha_text
