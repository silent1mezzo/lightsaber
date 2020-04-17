import os, random
from PIL import Image
import tweepy
from manifest import MANIFEST

IMAGE_PATH = "../images"
BLADE_PATH = "{}/blades".format(IMAGE_PATH)
HILT_PATH = "{}/hilts".format(IMAGE_PATH)
OUTPUT_PATH = "{}/lightsabers".format(IMAGE_PATH)

def fetch_lightsaber_parts():
    blade = "{}/{}".format(BLADE_PATH, random.choice(os.listdir(BLADE_PATH)))
    hilt = "{}/{}".format(HILT_PATH, random.choice(os.listdir(HILT_PATH)))

    return (blade, hilt)

def fetch_name(path):
    return path.split('/')[-1]

def resize_image(image):
    image_w, image_h = image.size
    image = image.resize((image_w*4, image_h*4), Image.ANTIALIAS)
    return image, image.size

def get_hilt_offset(hilt):
    hilt_name = hilt.split('.')[0]
    return MANIFEST['hilt'][hilt_name]['offsets']['blade']

def generate_lightsaber():
    hilt_name = blade_name = '.'
    output_filename = ''

    while blade_name.startswith('.') == True or hilt_name.startswith('.') == True or f"{output_filename}.png" in os.listdir(OUTPUT_PATH):
        blade_path, hilt_path = fetch_lightsaber_parts()
        blade_name = fetch_name(blade_path)
        hilt_name = fetch_name(hilt_path)

        # Create the filename here so we can check for uniqueness
        output_filename = f"{hilt_name.split('.')[0]}{blade_name.split('.')[0]}"
   
    blade = Image.open(blade_path, 'r')
    blade, (blade_w, blade_h) = resize_image(blade)
   
    hilt = Image.open(hilt_path, 'r')
    hilt, (hilt_w, hilt_h) = resize_image(hilt)
    
    img = Image.new("RGB", (1024, 512), (255, 255, 255))
    bg_w, bg_h = img.size

    hilt_offset = get_hilt_offset(hilt_name)
    blade_offset = ((bg_w - blade_w) // 2, (bg_h - blade_h - hilt_h + hilt_offset))
    hilt_offset = ((bg_w - hilt_w) // 2, bg_h-hilt_h)

    img.paste(blade, blade_offset, mask=blade)
    img.paste(hilt, hilt_offset, mask=hilt)
    img.save("{}/{}.png".format(OUTPUT_PATH, output_filename))

    return img, "{}/{}.png".format(OUTPUT_PATH, output_filename)


consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

lightsaber, path = generate_lightsaber()
#media = api.media_upload(path)
#api.update_status(media_ids=[media.media_id,])
