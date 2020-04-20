import os, random
from PIL import Image
import numpy as np
import tweepy
from manifest import MANIFEST
from name import NAMES

IMAGE_PATH = os.path.join(os.path.dirname(__file__), '../images')
BLADE_PATH = "{}/blades".format(IMAGE_PATH)
HILT_PATH = "{}/hilts".format(IMAGE_PATH)
BUTTON_PATH = "{}/buttons".format(IMAGE_PATH)
POMMEL_PATH = "{}/pommels".format(IMAGE_PATH)
OUTPUT_PATH = "{}/lightsabers".format(IMAGE_PATH)

AVERAGE_HILT_LENGTH = 25
AVERAGE_POMMEL_LENGTH = 3
AVERAGE_BLADE_LENGTH = 90

def generate_tweet_text(hilt, blade, pommel):
    hilt = hilt.split('.')[0]
    blade = blade.split('.')[0]
    pommel = pommel.split('.')[0]
    hilt_details = MANIFEST['hilt'][hilt]
    blade_details = MANIFEST['blade'][blade]
    pommel_details = MANIFEST['pommel'][pommel]

    hilt_length = hilt_details['length']
    pommel_length = pommel_details['length']

    total_length = hilt_length + pommel_length
    average_length = AVERAGE_HILT_LENGTH + AVERAGE_POMMEL_LENGTH
    blade_length = int(AVERAGE_BLADE_LENGTH * (total_length / average_length))

    title = blade_details['type']
    if type(title) is list:
        title = random.choice(title)

    name = f"{title} {random.choice(NAMES)}"

    tweet = f'''Owner: {name}
Hilt Length: {total_length} cm
Blade Length: {blade_length} cm
Blade Colour: {MANIFEST['blade'][blade]['colour']}
Kyber Crystal: {MANIFEST['blade'][blade]['crystal']}

#StarWars
'''

    return tweet

def convert_colours(img, hilt):
    hilt_name = hilt.split('.')[0]
    MANIFEST['hilt'][hilt_name]['offsets']['blade']
    img = img.convert('RGBA')
    data = np.array(img)

    red, green, blue, alpha = data.T
    primary = (red == 255) & (blue == 0) & (green == 0)
    secondary = (red == 0) & (blue == 255) & (green == 0)
    tertiary = (red == 0) & (blue == 0) & (green == 255)

    data[..., :-1][primary.T] = MANIFEST['hilt'][hilt_name]['colours']['primary']
    data[..., :-1][secondary.T] = MANIFEST['hilt'][hilt_name]['colours']['secondary']
    data[..., :-1][tertiary.T] = MANIFEST['hilt'][hilt_name]['colours']['tertiary']

    return Image.fromarray(data)

def fetch_lightsaber_parts():
    blade = "{}/{}".format(BLADE_PATH, random.choice(os.listdir(BLADE_PATH)))
    hilt = "{}/{}".format(HILT_PATH, random.choice(os.listdir(HILT_PATH)))
    button = "{}/{}".format(BUTTON_PATH, random.choice(os.listdir(BUTTON_PATH)))
    pommel = "{}/{}".format(POMMEL_PATH, random.choice(os.listdir(POMMEL_PATH)))

    return (blade, hilt, button, pommel)

def fetch_name(path):
    return path.split('/')[-1]

def resize_image(image):
    image_w, image_h = image.size
    image = image.resize((image_w*4, image_h*4), Image.ANTIALIAS)
    return image, image.size

def get_hilt_offset(hilt):
    hilt_name = hilt.split('.')[0]
    return MANIFEST['hilt'][hilt_name]['offsets']['blade']

def get_button_offset(hilt, pommel, button_w, button_h):
    hilt_name = hilt.split('.')[0]
    pommel_name = pommel.split('.')[0]
    between_x = MANIFEST['hilt'][hilt_name]['offsets']['button']['x']
    between_y = MANIFEST['hilt'][hilt_name]['offsets']['button']['y']
    return (random.randint(between_x[0], between_x[1]), random.randint(between_y[0], between_y[1]))

def generate_lightsaber():
    hilt_name = blade_name = button_name = pommel_name = '.'
    output_filename = ''

    while blade_name.startswith('.') == True or hilt_name.startswith('.') == True or button_name.startswith('.') == True or pommel_name.startswith('.') == True or f"{output_filename}.png" in os.listdir(OUTPUT_PATH):
        blade_path, hilt_path, button_path, pommel_path = fetch_lightsaber_parts()
        blade_name = fetch_name(blade_path)
        hilt_name = fetch_name(hilt_path)
        button_name = fetch_name(button_path)
        pommel_name = fetch_name(pommel_path)

        # Create the filename here so we can check for uniqueness
        output_filename = f"{hilt_name.split('.')[0]}{blade_name.split('.')[0]}{button_name.split('.')[0]}{pommel_name.split('.')[0]}"

    blade = Image.open(blade_path, 'r')
    blade_w, blade_h = blade.size
    #blade, (blade_w, blade_h) = resize_image(blade)
   
    hilt = Image.open(hilt_path, 'r')
    hilt_w, hilt_h = hilt.size
    #hilt, (hilt_w, hilt_h) = resize_image(hilt)

    button = Image.open(button_path, 'r')
    button = convert_colours(button, hilt_name)
    button_w, button_h = button.size
    #button, (button_w, button_h) = resize_image(button)

    pommel = Image.open(pommel_path, 'r')
    pommel = convert_colours(pommel, hilt_name)
    pommel_w, pommel_h = pommel.size
    #pommel, (pommel_w, pommel_h) = resize_image(pommel)
    
    max_width = max([blade_w, hilt_w, button_w, pommel_w])
  
    saber = Image.new("RGB", (max_width, blade_h+hilt_h+pommel_h), (255, 255, 255))
    bg_w, bg_h = saber.size

    pommel_offset = pommel_h
    hilt_offset = get_hilt_offset(hilt_name) - pommel_offset
    button_offset = get_button_offset(hilt_name, pommel_name, button_w, button_h)
    blade_offset = ((bg_w - blade_w) // 2, (bg_h - blade_h - hilt_h + hilt_offset))
    hilt_offset = ((bg_w - hilt_w) // 2, bg_h-hilt_h-pommel_offset)
    pommel_offset = ((bg_w - pommel_w) // 2, bg_h-pommel_h)

    # Paste all of the components onto the background
    saber.paste(blade, blade_offset, mask=blade)
    saber.paste(hilt, hilt_offset, mask=hilt)
    saber.paste(pommel, pommel_offset, mask=pommel)
    saber.paste(button, button_offset, mask=button)

    saber, (saber_w, saber_h) = resize_image(saber)

    img = Image.new("RGB", (1024, 512), (255, 255, 255))
    img_w, img_h = img.size
    img.paste(saber, ((img_w - saber_w) // 2, img_h-saber_h))
    img.save("{}/{}.png".format(OUTPUT_PATH, output_filename))

    return img, "{}/{}.png".format(OUTPUT_PATH, output_filename), (hilt_name, blade_name, pommel_name)


consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

lightsaber, path, parts = generate_lightsaber()

tweet_text = generate_tweet_text(parts[0], parts[1], parts[2])

media = api.media_upload(path)
api.update_status(status=tweet_text, media_ids=[media.media_id,])