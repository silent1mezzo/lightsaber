# lightsaber

lightsaber.py allows you to create a dynamically generated pixel-art lightsaber. You can read more about it [here](https://procrastinatingdev.com/using-python-to-generate-over-10000-unique-8-bit-lightsabers/)

## Installation

To install lightsaber.py simply clone the repo and install requirements.

```
git clone https://github.com/silent1mezzo/lightsaber.git
pip install -r requirements.txt
```

## Running

Running lightsaber.py will generate a lightsaber to `images/lightsabers` and print out the tweet details in console.

`python src/lightsaber.py` 

If you'd like to create a twitter bot like [DailyLightsaber](https://twitter.com/dailylightsaber) you'll need to add your twitter credentials as environment variables

```
export CONSUMER_KEY = ""
export CONSUMER_SECRET = ""
export ACCESS_TOKEN = ""
export ACCESS_TOKEN_SECRET = ""
```

Then run it with the --tweet argument

`python src/lightsaber.py --tweet`

## Contributing

If you'd like to contribute new designs open up an existing one in https://www.piskelapp.com/ to get the dimensions and then submit a PR with the new designs.
