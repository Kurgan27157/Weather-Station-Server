import sys
import sqlite3
import RPi.GPIO as GPIO
from datetime import datetime, date
import time
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085

#config sensor of humidity and temperature dht11
dht = Adafruit_DHT.DHT11
dht_pin=4

#config sensor of light sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)

#config sensor of  pressure bmp180
bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

#chec if just write values in terminal or save to database
if len(sys.argv) > 1:
    if(sys.argv[1] == 'justrun'):
        justrun=True
else:
    justrun=False


def readSensor():
    """
    :return: dict with all current values from sensors
    """

    #read values from dht11 sensor
    humidity_dht, temp_dht = Adafruit_DHT.read_retry(dht, dht_pin)
    #read values from bmp180 sensor
    pressure_bmp = bmp.read_pressure()
    altitude_bmp =int(bmp.read_altitude())
    slpressure_bmp = bmp.read_sealevel_pressure()
    temp_bmp = bmp.read_temperature()
    #read values from light sensor
    if (GPIO.input(17)==0):
        lights_on = 1
    else:
        lights_on = 0  
    #made avg, highes, lowest and variance of temperature
    avg_temp = ((temp_dht + temp_bmp)/2)
    temp_list = [temp_dht, temp_bmp]
    highest_temp = max(temp_list)
    lowest_temp = min(temp_list)
    variance_temp = float("{0:.2f}".format(highest_temp - lowest_temp))
    sensors = {
            'temp_dht' : temp_dht,
            'humidity_dht' : humidity_dht,
            'temp_bmp' : temp_bmp,
            'pressure_bmp' : pressure_bmp,
            'altitude_bmp' : altitude_bmp,
            'sea_level_pressure_bmp' : slpressure_bmp,
            'lights_on' : lights_on,
            'avg_temp' : avg_temp,
            'highest_temp' : highest_temp,
            'lowest_temp' : lowest_temp,
            'variance_temp' : variance_temp
        }
    return sensors


def jrun(justrun, sensors_data):
    """
    Write current values from all sensors
    :param justrun:
    :param sensors_data:
    :return:
    """
    if justrun:
        print 'DHT11:'
        print 'Temp ={0:0.1f}*C'.format(sensors_data['temp_dht']) 
        print 'Humidity={0:0.1f}%'.format(sensors_data['humidity_dht'])
        print 'BMP180:'
        print 'Temp = {0:0.1f} *C'.format(sensors_data['temp_bmp'])
        print 'Pressure = {0:0.1f} Pa'.format(sensors_data['pressure_bmp'])
        print 'Altitude = {0:0.1f} m'.format(sensors_data['altitude_bmp'])
        print 'Sealevel Pressure = {0:0.1f} Pa'.format(sensors_data['sea_level_pressure_bmp'])
        print 'Swiatlo - ', sensors_data['lights_on']
        print 'Average Temp: ' + str(sensors_data['avg_temp'])
        print 'Highest Temp: ' + str(sensors_data['highest_temp'])
        print 'Lowest Temp: '  + str(sensors_data['lowest_temp'])
        print 'Variance Temp: ' + str(sensors_data['variance_temp'])


def into_db(sensors_data):
    """
    save all current values from sensors into database
    :param sensors_data:
    :return:
    """
    if justrun!=True:

        conn=sqlite3.connect('Weather.db')
        curs=conn.cursor()
        curs.execute("INSERT INTO dht11(timestamp, temp, humidity) values(datetime('now','localtime'),?,?)",(sensors_data['temp_dht'],sensors_data['humidity_dht']))
   
        curs.execute("INSERT INTO bmp180(timestamp, temp, pressure, slpressure, altitude) values(datetime('now','localtime'),?,?,?,?)", (sensors_data['temp_bmp'],sensors_data['pressure_bmp'], sensors_data['sea_level_pressure_bmp'], sensors_data['altitude_bmp']))
        curs.execute("INSERT INTO lights(timestamp, lightsOn) values(datetime('now','localtime'),?)", (sensors_data['lights_on'],))
        curs.execute("INSERT INTO mixed(timestamp,avgtemp, lowesttemp, highesttemp, variancetemp) values(datetime('now','localtime'),?,?,?,?)", (sensors_data['avg_temp'],sensors_data['lowest_temp'],sensors_data['highest_temp'],sensors_data['variance_temp']))
    
        # commit the changes
        conn.commit()

        conn.close()

while True:
    sensors_data = readSensor()
    jrun(justrun, sensors_data)
    into_db(sensors_data)
    time.sleep(60)
