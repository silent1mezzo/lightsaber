import os, random
from PIL import Image
import tweepy
from manifest import MANIFEST
from name import NAMES

IMAGE_PATH = "../images"
BLADE_PATH = "{}/blades".format(IMAGE_PATH)
HILT_PATH = "{}/hilts".format(IMAGE_PATH)
BUTTON_PATH = "{}/buttons".format(IMAGE_PATH)
OUTPUT_PATH = "{}/lightsabers".format(IMAGE_PATH)

AVERAGE_HILT_LENGTH = 28
AVERAGE_BLADE_LENGTH = 300

def generate_tweet_text(hilt, blade):
    hilt = hilt.split('.')[0]
    blade = blade.split('.')[0]
    hilt_details = MANIFEST['hilt'][hilt]
    blade_details = MANIFEST['blade'][blade]

    hilt_length = hilt_details['length']
    blade_length = int(AVERAGE_BLADE_LENGTH * (hilt_length / AVERAGE_HILT_LENGTH))

    title = blade_details['type']
    if type(title) is list:
        title = random.choice(title)

    name = f"{title} {random.choice(NAMES)}"

    tweet = f'''Owner: {name}
Hilt Length: {hilt_length} cm
Blade Length: {blade_length} cm
Blade Colour: {MANIFEST['blade'][blade]['colour']}
Kyber Crystal: {MANIFEST['blade'][blade]['crystal']}

#StarWars
'''

    return tweet

def fetch_lightsaber_parts():
    blade = "{}/{}".format(BLADE_PATH, random.choice(os.listdir(BLADE_PATH)))
    hilt = "{}/{}".format(HILT_PATH, random.choice(os.listdir(HILT_PATH)))
    button = "{}/{}".format(BUTTON_PATH, random.choice(os.listdir(BUTTON_PATH)))

    return (blade, hilt, button)

def fetch_name(path):
    return path.split('/')[-1]

def resize_image(image):
    image_w, image_h = image.size
    image = image.resize((image_w*4, image_h*4), Image.ANTIALIAS)
    return image, image.size

def get_hilt_offset(hilt):
    hilt_name = hilt.split('.')[0]
    return MANIFEST['hilt'][hilt_name]['offsets']['blade']

def get_button_offset(hilt, button_w, button_h):
    hilt_name = hilt.split('.')[0]
    between_x = MANIFEST['hilt'][hilt_name]['offsets']['button']['x']
    between_y = MANIFEST['hilt'][hilt_name]['offsets']['button']['y']

    return (random.randint(between_x[0], between_x[1]), random.randint(between_y[0], between_y[1]))

def generate_lightsaber():
    hilt_name = blade_name = button_name = '.'
    output_filename = ''

    while blade_name.startswith('.') == True or hilt_name.startswith('.') == True or button_name.startswith('.') == True or f"{output_filename}.png" in os.listdir(OUTPUT_PATH):
        blade_path, hilt_path, button_path = fetch_lightsaber_parts()
        blade_name = fetch_name(blade_path)
        hilt_name = fetch_name(hilt_path)
        button_name = fetch_name(button_path)

        # Create the filename here so we can check for uniqueness
        output_filename = f"{hilt_name.split('.')[0]}{blade_name.split('.')[0]}{button_name.split('.')[0]}"

    blade = Image.open(blade_path, 'r')
    blade, (blade_w, blade_h) = resize_image(blade)
   
    hilt = Image.open(hilt_path, 'r')
    hilt, (hilt_w, hilt_h) = resize_image(hilt)

    button = Image.open(button_path, 'r')
    button, (button_w, button_h) = resize_image(button)
    
    img = Image.new("RGB", (1024, 512), (255, 255, 255))
    bg_w, bg_h = img.size

    hilt_offset = get_hilt_offset(hilt_name)
    button_offset = get_button_offset(hilt_name, button_w, button_h)
    blade_offset = ((bg_w - blade_w) // 2, (bg_h - blade_h - hilt_h + hilt_offset))
    hilt_offset = ((bg_w - hilt_w) // 2, bg_h-hilt_h)
    
    img.paste(blade, blade_offset, mask=blade)
    img.paste(hilt, hilt_offset, mask=hilt)
    img.paste(button, button_offset, mask=button)
    
    img.save("{}/{}.png".format(OUTPUT_PATH, output_filename))

    return img, "{}/{}.png".format(OUTPUT_PATH, output_filename), (hilt_name, blade_name)


consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

lightsaber, path, parts = generate_lightsaber()
import subprocess
subprocess.call(['open', path])
tweet_text = generate_tweet_text(parts[0], parts[1])
print(tweet_text)
#media = api.media_upload(path)
#api.update_status(media_ids=[media.media_id,])
