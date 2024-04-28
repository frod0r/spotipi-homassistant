import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import requests
from io import BytesIO
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import os
import configparser
from datetime import datetime, timedelta

from WeatherDisplay import WeatherDisplay


def main() -> int:

	username = sys.argv[1]
	token_path = sys.argv[2]

	# Configuration file
	project_dir = os.path.dirname(__file__)
	filename = os.path.join(project_dir, '../config/rgb_options.ini')
	icon_dir = os.path.join(project_dir, '../weather_icons/')
	text_color = graphics.Color(240, 230, 220)

	# Configures logger for storing song data
	logging.basicConfig(
		format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log', level=logging.INFO)
	logger = logging.getLogger('spotipy_logger')

	# automatically deletes logs more than 2000 bytes
	handler = RotatingFileHandler('spotipy.log', maxBytes=2000, backupCount=3)
	logger.addHandler(handler)

	# Configuration for the matrix
	config = configparser.ConfigParser()
	config.read(filename)

	options = RGBMatrixOptions()
	options.rows = int(config['DEFAULT']['rows'])
	options.cols = int(config['DEFAULT']['columns'])
	options.chain_length = int(config['DEFAULT']['chain_length'])
	options.parallel = int(config['DEFAULT']['parallel'])
	options.hardware_mapping = config['DEFAULT']['hardware_mapping']
	options.gpio_slowdown = int(config['DEFAULT']['gpio_slowdown'])
	options.brightness = int(config['DEFAULT']['brightness'])
	options.led_rgb_sequence = config['DEFAULT']['led_rgb_sequence']

	lat = config['DEFAULT']['lat']
	lon = config['DEFAULT']['lon']
	units = config['DEFAULT']['units']
	appid = config['DEFAULT']['appid']
	weather_request_frequency = int(config['DEFAULT']['weather_request_frequency'])
	toggle_frequency = int(config['DEFAULT']['toggle_frequency'])


	font = graphics.Font()
	font_small = graphics.Font()
	font_path = os.path.join(project_dir, '../fonts/5x8.bdf')
	font_small_path = os.path.join(project_dir, '../fonts/4x6.bdf')
	print(font_path)
	font.LoadFont(font_path)
	font_small.LoadFont(font_small_path)

	default_image = os.path.join(project_dir, config['DEFAULT']['default_image'])
	print(default_image)
	matrix = RGBMatrix(options=options)
	canvas = matrix.CreateFrameCanvas()

	weather_disp = WeatherDisplay(
		lat=lat,
		lon=lon,
		units=units,
		appid=appid,
		weather_request_frequency=weather_request_frequency,
		toggle_frequency=toggle_frequency,
		icon_dir=icon_dir,
		font=font,
		font_small=font_small
	)

	last_url = ""
	image_url = None
	last_spotify_refresh = datetime.now()
	try:
		while True:
			try:
				now = datetime.now()
				if now - last_spotify_refresh > timedelta(seconds=1):
					image_url = getSongInfo(username, token_path)[1]
					last_spotify_refresh = now
				if image_url is not None:
					if image_url == last_url:
						time.sleep(1)
						continue
					last_url = image_url
					response_image = requests.get(image_url)
					image = Image.open(BytesIO(response_image.content))
					image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
					# image.thumbnail((matrix.width/2, matrix.height/2), Image.ANTIALIAS)
					canvas.SetImage(image.convert('RGB'))
					time.sleep(1)
				else:
					weather_disp.display_weather_panel(canvas)
					time.sleep(0.5)
				canvas = matrix.SwapOnVSync(canvas)
				canvas.Clear()
			except Exception as e:
				print(str(e))
				image = Image.open(default_image)
				image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
				canvas.SetImage(image.convert('RGB'))
				i = 1
				for msg_part in str(e).split():
					graphics.DrawText(canvas, font, 0, 8 * i, text_color, msg_part)
					i = i + 1
				canvas = matrix.SwapOnVSync(canvas)
				time.sleep(5)
				canvas.Clear()
	except KeyboardInterrupt:
		return 0


if len(sys.argv) > 2:
	if __name__ == '__main__':
		sys.exit(main())
else:
	print("Usage: %s username" % (sys.argv[0],))
	sys.exit()
