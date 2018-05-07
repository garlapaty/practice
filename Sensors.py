                                          import RPi.GPIO as GPIO
import time
import pymongo
import sys
from pymongo import MongoClient
import dht11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

DO_pin = 17
AO_pin = 0 #flame sensor AO connected to ADC chanannel 0
# change these as desired – they’re the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
pin = 4
GPIO.setup(pin,GPIO.OUT)
# photoresistor connected to adc #0
photo_ch = 1

#vibration sensor
channel = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21, 1)

#port init
def init():
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.output(buzzer,GPIO.HIGH)
GPIO.setup(DO_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
pass
#read SPI data from MCP3008(or MCP3204) chip,8 possible adc’s (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
if ((adcnum > 7) or (adcnum < 0)):
return -1
GPIO.output(cspin, True)
GPIO.output(clockpin, False) # start clock low
GPIO.output(cspin, False) # bring CS low

commandout = adcnum
commandout |= 0x18 # start bit + single-ended bit
commandout <<= 3 # we only need to send 5 bits here
for i in range(5):
if (commandout & 0x80):
GPIO.output(mosipin, True)
else:
GPIO.output(mosipin, False)
commandout <<= 1
GPIO.output(clockpin, True)
GPIO.output(clockpin, False)

adcout = 0
# read in one empty bit, one null bit and 10 ADC bits
for i in range(12):
GPIO.output(clockpin, True)
GPIO.output(clockpin, False)
adcout <<= 1
if (GPIO.input(misopin)):
adcout |= 0x1

GPIO.output(cspin, True)
adcout >>= 1 # first bit is ‘null’ so drop it
return adcout
#Storing data into database
def fire_data(F_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_fire = db[document]
db.drop_collection(document)
sensor_fire.insert_one(F_DATA)
#print(“Data written”)
client.close()                                                                                                                                            def fire():
flame_value = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
if GPIO.input(DO_pin)==False:
print (“***********”)
print (“* Safe! *”)
print(‘ ‘)
F_DATA = {
‘WARNING’:’SAFE!!!’
}
fire_data(F_DATA,”sensor_fire”)
else:
print (“***********”)
print (“* Fire! *”)
print (“fire ADC value is: ” + str(“%.1f”%((1024-flame_value)/1024.*3.3))+”V”)
print (“***********”)
print (‘ ‘)
FR_DATA = {
‘WARNING’:’FIRE!!!’
}
firee_data(FR_DATA,”sensor_fire”)
def firee_data(FR_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_fire = db[document]
db.drop_collection(document)
sensor_fire.insert_one(FR_DATA)
#print(“Data written”)
client.close()                                                                                                                                            # storing data in database                                                                                                                    def waterr_data(W_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_water = db[document]
db.drop_collection(document)
sensor_water.insert_one(W_DATA)
#print(“Data written”)
client.close()
def water():
adc_value=readadc(photo_ch, SPICLK, SPIMOSI, SPIMISO, SPICS)
if adc_value <= 10:
print(“no leak”)
W_DATA = {
‘MESSAGE’:’No Leak’
}
waterr_data(W_DATA,”sensor_water”)
else:
print(“water leak”)
WT_DATA = {
‘MESSAGE’:’Water Leak’
}
water_data(WT_DATA,”sensor_water”)
def water_data(WT_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_water = db[document]
db.drop_collection(document)
sensor_water.insert_one(WT_DATA)
#print(“Data written”)
client.close()
time.sleep(1)                                                                                                                                            def temp():
instance = dht11.DHT11(pin = 4)
result = instance.read()
if result.is_valid():
print(“Temperature: %d C” % result.temperature)
print(“Humidity: %d %%” % result.humidity)
T_DATA = {
‘Temeprature’: result.temperature,
‘Humidity’: result.humidity
}
store_data(T_DATA,”sensor_DHT11?)
def store_data(T_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_DHT11 = db[document]
db.drop_collection(document)
sensor_DHT11.insert_one(T_DATA)
#print(“Data written”)
client.close()
#Storing Vibration Data
def vib_data(V_DATA,document):
MONGODB_URI = “mongodb://test:test@ds159217.mlab.com:59217/sample”
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database(‘sample’)
sensor_vibration = db[document]
db.drop_collection(document)
sensor_vibration.insert_one(V_DATA)
#print(“Data written”)
client.close()                                                                                                                                            def callback(channel):
while(GPIO.input(channel)):
print (“Movement Detected!”)
V_DATA = {
‘Movement’ : ‘Motion Detected’
}
vib_data(V_DATA,”sensor_vibration”)
GPIO.output(21, 0)
time.sleep(3)
GPIO.output(21, 1)
if __name__ ==’__main__’:
try:
init()
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300) # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback) # assign function to GPIO PIN, Run function on change
while(True):
V_DATA = {
‘Movement’ : ‘SAFE’
}
vib_data(V_DATA,”sensor_vibration”)
water()
fire()
temp()
except KeyboardInterrupt:
pass
GPIO.cleanup()