import os, random
from pathlib import Path, PurePath
from PIL import Image
import numpy as np
import argparse
import tweepy
import sentry_sdk
from manifest import MANIFEST
from name import NAMES
from utils import get_crystal, get_path, get_title

IMAGE_PATH = Path(__file__).parent.absolute() / "../images"
BLADE_PATH = IMAGE_PATH / "blades"
HILT_PATH = IMAGE_PATH / "hilts"
BUTTON_PATH = IMAGE_PATH / "buttons"
POMMEL_PATH = IMAGE_PATH / "pommels"
OUTPUT_PATH = IMAGE_PATH / "lightsabers"

AVERAGE_HILT_LENGTH = 25
AVERAGE_POMMEL_LENGTH = 3
AVERAGE_BLADE_LENGTH = 90

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)


def generate_tweet_text(hilt, blade, pommel):
    hilt_details = MANIFEST["hilt"][hilt]
    blade_details = MANIFEST["blade"][blade]
    pommel_details = MANIFEST["pommel"][pommel]

    hilt_length = hilt_details["length"]
    pommel_length = pommel_details["length"]

    total_length = hilt_length + pommel_length
    average_length = AVERAGE_HILT_LENGTH + AVERAGE_POMMEL_LENGTH
    blade_length = int(AVERAGE_BLADE_LENGTH * (total_length / average_length))

    title = get_title(blade_details)

    crystal = get_crystal(blade_details)

    name = f"{title} {random.choice(NAMES)}"

    tweet = f"""Owner: {name}
Hilt Length: {total_length} cm
Blade Length: {blade_length} cm
Blade Colour: {MANIFEST['blade'][blade]['colour']}
Kyber Crystal: {crystal}

#StarWars #lightsaber #{title}
"""

    return tweet


def convert_colours(img, hilt):
    MANIFEST["hilt"][hilt]["offsets"]["blade"]
    img = img.convert("RGBA")
    data = np.array(img)

    red, green, blue, alpha = data.T
    primary = (red == 255) & (blue == 0) & (green == 0)
    secondary = (red == 0) & (blue == 255) & (green == 0)
    tertiary = (red == 0) & (blue == 0) & (green == 255)

    data[..., :-1][primary.T] = MANIFEST["hilt"][hilt]["colours"]["primary"]
    data[..., :-1][secondary.T] = MANIFEST["hilt"][hilt]["colours"]["secondary"]
    data[..., :-1][tertiary.T] = MANIFEST["hilt"][hilt]["colours"]["tertiary"]

    return Image.fromarray(data)


def fetch_lightsaber_parts(hilt, blade, button, pommel):
    hilt = get_path(hilt, HILT_PATH)
    blade = get_path(blade, BLADE_PATH)
    button = get_path(button, BUTTON_PATH)
    pommel = get_path(pommel, POMMEL_PATH)

    return (blade, hilt, button, pommel)


def fetch_name(path):
    return PurePath(path).stem


def resize_image(image):
    image_w, image_h = image.size

    # Don't allow the height of the image to go above 130px. Once scaled up this makes sure the blade doesn't go out of frame
    image_h = min(image_h, 130)
    image = image.resize((image_w * 4, image_h * 4), Image.ANTIALIAS)
    return image, image.size


def get_hilt_offset(hilt):
    return MANIFEST["hilt"][hilt]["offsets"]["blade"]


def get_button_offset(hilt, pommel, button_w, button_h):
    between_x = MANIFEST["hilt"][hilt]["offsets"]["button"]["x"]
    between_y = MANIFEST["hilt"][hilt]["offsets"]["button"]["y"]
    return (
        random.randint(between_x[0], between_x[1]),
        random.randint(between_y[0], between_y[1]),
    )


def generate_lightsaber(hilt, blade, button, pommel):
    hilt_name = hilt
    blade_name = blade
    button_name = button
    pommel_name = pommel
    output_filename = ""

    while (
        blade_name.startswith(".") == True
        or hilt_name.startswith(".") == True
        or button_name.startswith(".") == True
        or pommel_name.startswith(".") == True
        or Path(f"{OUTPUT_PATH}/{output_filename}.png").exists()
    ):
        blade_path, hilt_path, button_path, pommel_path = fetch_lightsaber_parts(
            hilt, blade, button, pommel
        )
        blade_name = fetch_name(blade_path)
        hilt_name = fetch_name(hilt_path)
        button_name = fetch_name(button_path)
        pommel_name = fetch_name(pommel_path)

        # Create the filename here so we can check for uniqueness
        output_filename = f"{hilt_name}{blade_name}{button_name}{pommel_name}"

    blade = Image.open(blade_path, "r")
    blade_w, blade_h = blade.size

    hilt = Image.open(hilt_path, "r")
    hilt_w, hilt_h = hilt.size

    button = Image.open(button_path, "r")
    button = convert_colours(button, hilt_name)
    button_w, button_h = button.size

    pommel = Image.open(pommel_path, "r")
    pommel = convert_colours(pommel, hilt_name)
    pommel_w, pommel_h = pommel.size

    max_width = max([blade_w, hilt_w, button_w, pommel_w])

    saber = Image.new("RGB", (max_width, blade_h + hilt_h + pommel_h), (255, 255, 255))
    bg_w, bg_h = saber.size

    pommel_offset = pommel_h
    hilt_offset = get_hilt_offset(hilt_name) - pommel_offset
    button_offset = get_button_offset(hilt_name, pommel_name, button_w, button_h)
    blade_offset = ((bg_w - blade_w) // 2, (bg_h - blade_h - hilt_h + hilt_offset))
    hilt_offset = ((bg_w - hilt_w) // 2, bg_h - hilt_h - pommel_offset)
    pommel_offset = ((bg_w - pommel_w) // 2, bg_h - pommel_h)

    # Paste all of the components onto the background
    saber.paste(blade, blade_offset, mask=blade)
    saber.paste(hilt, hilt_offset, mask=hilt)
    saber.paste(pommel, pommel_offset, mask=pommel)
    saber.paste(button, button_offset, mask=button)

    saber, (saber_w, saber_h) = resize_image(saber)

    img = Image.new("RGB", (1024, 512), (255, 255, 255))
    img_w, img_h = img.size
    img.paste(saber, ((img_w - saber_w) // 2, img_h - saber_h))
    img.save("{}/{}.png".format(OUTPUT_PATH, output_filename))

    return (
        img,
        "{}/{}.png".format(OUTPUT_PATH, output_filename),
        (hilt_name, blade_name, pommel_name),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--tweet", action="store_true", help="Should this tweet out the results"
    )
    parser.add_argument(
        "--open", action="store_true", help="Open the files automatically"
    )
    parser.add_argument("--hilt", nargs="?", default=".", help="Use a specific hilt")
    parser.add_argument("--blade", nargs="?", default=".", help="Use a specific blade")
    parser.add_argument(
        "--pommel", nargs="?", default=".", help="Use a specific pommel"
    )
    parser.add_argument(
        "--button", nargs="?", default=".", help="Use a specific button"
    )

    args = parser.parse_args()
    lightsaber, path, parts = generate_lightsaber(
        hilt=args.hilt, blade=args.blade, pommel=args.pommel, button=args.button
    )

    if args.open:
        import subprocess

        subprocess.call(["open", path])

    tweet_text = generate_tweet_text(parts[0], parts[1], parts[2])
    if not args.tweet:
        print(tweet_text)
    else:
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")

        access_token = os.getenv("ACCESS_TOKEN")
        access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        media = api.media_upload(path)
        api.update_status(status=tweet_text, media_ids=[media.media_id,])
