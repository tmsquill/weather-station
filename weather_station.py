#!/usr/bin/env python

"""
Author: Troy Squillaci (troysquillaci.me)

Raspberry Pi Weather Station

This simple script enables a Raspberry Pi to be used as a basic weather
station, capable of reporting temperatue and humidity readings to Weather
Underground (https://www.wunderground.com/). This project utilizes the
Adafruit AM2302 (Temperature / Humidity) sensor.
"""

import Adafruit_DHT
import argparse
import datetime
import sys
import time

from urllib.parse import urlencode
from urllib.request import urlopen

WU_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"


def read_sensor():

    """
    Attempt to take a sensor reading, using the read_retry method will attempt
    up to 15 times to get a sensor reading (with two second pauses between
    attempts).
    """

    return Adafruit_DHT.read_retry(sensor, pin)


def to_fahrenheit(temp):

    """
    Converts a temperature in celsius to fahrenheit.
    """

    return (temp * 1.8) + 32


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--interval', type=float, required=True,
                        help='interval (in minutes) to read sensor data')
    parser.add_argument('-s', '--station_id', type=str,
                        help='the station id assigned by Weather Underground')
    parser.add_argument('-k', '--station_key', type=str,
                        help='the station key assigned by Weather Underground')
    parser.add_argument('-u', '--upload', action='store_true', default=False,
                        help='upload data to Weather Underground')

    args = parser.parse_args()

    # Specify the correct sensor variant.
    sensor = Adafruit_DHT.AM2302

    # Specify the pin the sensor is connected to on the Raspberry Pi. This can
    # be changed. See https://pinout.xyz/pinout/# for more information.
    pin = 4

    # Used to allow for constant temperature recordings, but only periodic
    # uploads to Weather Underground.
    prev_min = datetime.datetime.now().minute
    prev_min -= 1

    if prev_min == 0:

        prev_min = 59

    while True:

        cur_min = datetime.datetime.now().minute

        # Attempt to read the sensor for humidity and temperature.
        humidity, temperature = read_sensor()

        # Convert the temperature to fahrenheit.
        temperature = to_fahrenheit(temperature)

        print(f'Temperature: {temperature}, Humidity: {humidity}')

        if cur_min != prev_min:

            prev_min = cur_min

            if (cur_min == 0) or ((cur_min % args.interval) == 0):

                if humidity and temperature:

                    # Upload the sensor readings to Weather Underground.
                    if args.upload:

                        print('Uploading data to Weather Underground...')

                        weather_data = {
                            "action": "updateraw",
                            "ID": args.station_id,
                            "PASSWORD": args.station_key,
                            "dateutc": "now",
                            "tempf": str(temperature),
                            "humidity": str(humidity)
                        }

                        try:

                            upload_url = f'{WU_URL}?{urlencode(weather_data)}'

                            response = urlopen(upload_url)
                            print(f'Weather Underground: {response.read()}')
                            response.close()

                        except Exception:

                            print('Exception:', sys.exc_info()[0])
                    else:

                        print('Skipping upload to Weather Underground.')

                else:

                    print('Unable to read sensor data...')

        # Time between samples in minutes, should be somewhat large to avoid
        # reading issue with the Adafruit AM2302 sensor.
        time.sleep(5)
