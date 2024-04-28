# Spotipi & Weather managed by Homeassistant
![Showcase](images/Showcase.jpg)
### Overview
This project is to display spotify cover art on 64x64 led matrix from the Spotify web api.
When not playing music it should display weather information.

Note: For smaller displays you might want to rearrange the weather display elements.
If you have trouble doing that just open an issue with your idea and I'll see what I can do.
### Differences in this fork
* Support for more Hardware
  * The original repo automatically installed Adafruit's fork of the hzeller/rpi-rgb-led-matrix library used to communicate with the hat, I replaced this with references to the proper documentation to enable an easy install on non-adafruit hardware as well.
  * Added led_rgb_sequence as a configurable option. Some not all panels control their leds via RGB, mine for example uses GBR, if colors look weird on yours chances are, you have a different sequence of R G and B.
* Added a weather display using OpenWeatherMap for when no music is playing
* Removed the local flask control and replaced with a mqtt module that registers as a Homeassistant Lamp
  * In the future I plan to modularize this so you can use whatever you want, but for now Homeassistant it is.
* Added error display to show what is wrong, when something goes wrong.
* Originally I included some fixes here that since then are now also present in the original repo, although in some cases implemented in a different way, like the upgrade to python3, or reducing the amount of requests to the Spotify API

### Getting Started
* Create a new application within the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications) <br />
* Edit the settings of the application within the dashboard.
    * Set the redirect uri to any local url such as http://127.0.0.1/callback
* Before logging into the raspberry pi, you will need to generate an authentication token.
* To do this, you are going to want to clone my spotipi repository on your main computer with access to a web browser.
```
git clone  https://github.com/frod0r/spotipi-homeassistant.git
```
* Next go ahead and change into the directory using 
```
cd spotipi
```
* Run the generate token script and enter the prompted spotify credentials using
```
bash generate-token.sh
```
* This will generate a file named `.cache-<username>`
* You are going to want to scp this file over to your raspberry pi, for example:
```
scp .cache-<username> pi@spotipy.local:/home/pi
```
* Get yourself some openweathermap credentials by registering an account and heading over to [the api keys section](https://home.openweathermap.org/api_keys) (the onecall-api we use is included in the free default api key)
* Enter your location data and api-key in ```config/rgb_options.ini```.
* On the Raspberry Pi, setup the LED-Matrix, following [the guide provided by the rpi-led-matrix project](https://github.com/hzeller/rpi-rgb-led-matrix) if you are using an adafruit hat, also have a look at [their guide](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi)
* Set up pyhton3 bindings following [this guide](https://github.com/hzeller/rpi-rgb-led-matrix/blob/a93acf26990ad6794184ed8c9487ab2a5c39cd28/bindings/python/README.md). Confirm it working by executing one of the [python samples](
rpi-rgb-led-matrix/bindings/python/samples/)
* Clone the spotipi repository to your raspberrypi
```
git clone https://github.com/frod0r/spotipi-homeassistant.git
```
* Move the token file to the repository root
```
mv <path_to_cache_file> <path_to_cloned_repository>
```
* Install the systemd-units: <br />
```
cd spotipi
sudo ./setup.sh
```
* Set up mqtt in home assistant if you haven't already and let it discover your smart led martix


### A note on OpenWeatherMap API Cost

Firstly: You should be able to use this project for free (aside from the hardware cost).
Unfortunately OpenWeatherMap is about to shut down their 2.5 OneCall API, which we could use for totally free, and replaces it with the 3.0 OneCall API. It still has the same amount of free calls per day, however if you go over the limit now, you pay as you go, and thus they also require you to set up payment info.

You do have 1000 free calls per day (that's 0.694 calls per minute or one call every 1.44 minutes), but after that you pay 14 cents per 100 calls. Per default, this software calls the OpenWeatherMap OneCall 3.0 API once every 5 minutes. This is configurable as the option `weather_request_frequency` in `rgb_options.ini`.

Luckily in the ["Billing Plan" section](https://home.openweathermap.org/subscriptions) of you account you can set a limit on how many calls per day you want to allow for. You can set this to 1000 calls to avoid actually getting billed.

I looked into other weather api providers as well:
* https://developer.accuweather.com/packages accuweather allows for 50 calls per day and requires branding and linking to their site.
* https://www.meteosource.com/pricing meteosource allows for 400 calls per day, and requires attribution text + backlinks to their site.
* https://api.windy.com/point-forecast windy only offers a trial plan with 500 calls a day, unsure if this would be okay to use permanently in a personal project like this.