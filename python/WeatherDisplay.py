import requests
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import os
from datetime import datetime, timedelta

text_color = graphics.Color(240, 230, 220)
black_img = Image.new('RGBA', (16, 16)).convert('RGBA')
iconMap = {
	'01d': 'sun.png',
	'01n': 'half-moon.png',
	'02d': 'cloudy_2.png',
	'02n': 'cloudy-night.png',
	'03d': 'cloud.png',
	'03n': 'cloud.png',
	'04d': 'cloudy_broken.png',
	'04n': 'cloudy_broken.png',
	'09d': 'rain_shower.png',
	'09n': 'rain_shower.png',
	'10d': 'rain.png',
	'10n': 'rain.png',
	'11d': 'storm.png',
	'11n': 'storm_1.png',
	'13d': 'snowflake.png',
	'13n': 'snowflake.png',
	'50d': 'wind.png',
	'50n': 'wind.png'}


class WeatherDisplay:
	def __init__(
			self,
			lat,
			lon,
			units,
			appid,
			weather_request_frequency,
			toggle_frequency,
			icon_dir,
			font,
			font_small
	):
		self.query = {
			'lat': lat, 'lon': lon, 'units': units, 'exclude': 'minutely,alerts',
			'appid': appid}
		self.weather_request_frequency = weather_request_frequency # Time in minutes on how often to send a request to the weather api
		self.toggle_frequency = toggle_frequency # Time in seconds on how often to toggle between displaying temperature and time/ weekdays
		self.icon_dir = icon_dir
		self.font = font
		self.font_small = font_small
		response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=self.query, timeout=5)
		self.response_json = response.json()
		self.last_weather_refresh = datetime.now()
		self.last_temp_display_toggle = datetime.now()
		self.display_temp = False

	def get_icon(self, icon_name):
		icon_path = iconMap[icon_name]
		if not icon_path:
			icon_path = 'thunder.png'
		return Image.alpha_composite(black_img, Image.open(os.path.join(self.icon_dir + icon_path)).convert(
			'RGBA')).convert('RGB')

	def refresh_weather(self):
		response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=self.query, timeout=5)
		self.response_json = response.json()

	def display_weather_panel(self, canvas):
		now = datetime.now()
		if now - self.last_weather_refresh > timedelta(minutes=self.weather_request_frequency):
			self.refresh_weather()
			self.last_weather_refresh = now
			print('refreshed')
		if now - self.last_temp_display_toggle > timedelta(seconds=self.toggle_frequency):
			self.display_temp = ~self.display_temp
			self.last_temp_display_toggle = now
		length = self.display_time(canvas, now)
		self.display_weather(canvas, length)

	def display_time(self, canvas, now):
		now_text = now.strftime('%H:%M')
		secs_text = now.strftime(':%S')
		secs = int(now.strftime('%-S'))
		length = graphics.DrawText(canvas, self.font, 0, 8, text_color, now_text)
		graphics.DrawText(
			canvas, self.font, 10, 16,
			graphics.Color((int(secs * 4.25) + 125) % 255, 255 - int(secs * 4.25) % 255, int(secs * 4.25) % 255),
			secs_text)
		return length

	def display_weather(self, canvas, length):
		main_icon_name = self.response_json['current']['weather'][0]['icon']
		main_icon = self.get_icon(main_icon_name)
		canvas.SetImage(main_icon, length, 0)
		graphics.DrawText(
			canvas, self.font_small, length + 18, 8, text_color, str(self.response_json['current']['temp']) + '°')
		graphics.DrawText(
			canvas, self.font_small, length + 18, 16, text_color, str(self.response_json['current']['humidity']) + '%')
		for i in range(1, 5):
			icon_name = self.response_json['hourly'][i]['weather'][0]['icon']
			time_text = datetime.fromtimestamp(self.response_json['hourly'][i]['dt']).strftime('%Hh')
			if self.display_temp:
				time_text = f"{round(self.response_json['hourly'][i]['temp'])}°"
			canvas.SetImage(self.get_icon(icon_name), 16 * (i - 1), 16)
			graphics.DrawText(canvas, self.font_small, 16 * (i - 1) + 2, 40 - 2, text_color, time_text)
			icon_name_daily = self.response_json['daily'][i]['weather'][0]['icon']
			time_text_daily = datetime.fromtimestamp(self.response_json['daily'][i]['dt']).strftime('%a')
			if self.display_temp:
				time_text_daily = f"{round(self.response_json['daily'][i]['temp']['day'])}°"
			canvas.SetImage(self.get_icon(icon_name_daily), 16 * (i - 1), 40)
			graphics.DrawText(canvas, self.font_small, 16 * (i - 1) + 2, 64 - 2, text_color, time_text_daily)
