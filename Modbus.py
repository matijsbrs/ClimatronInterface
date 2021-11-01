#!/usr/bin/env python3
import select
import threading
import minimalmodbus
import serial
import time
from ModbusPSoC import PSoC
from HVAC import Valve
import paho.mqtt.client as mqtt

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("automation/set/climatronic/#")


def on_message(client, userdata, msg):
    topic = msg.topic.split("/")
    # print ("Topic:{} value:{}".format(msg.topic, msg.payload) )
    if (str(topic[-1]) == "highflowshort"):
        if (msg.payload == b'true'):
            AirValve.HighFlowShort()
        else:
            AirValve.LowFlow()
        
    if (str(topic[-1]) == "highflowmedium"):
        if (msg.payload == b'true'):
            AirValve.HighFlowMedium()
        else:
            AirValve.LowFlow()
        
    if (str(topic[-1]) == "highflowlong"):
        if (msg.payload == b'true'):
            AirValve.HighFlowLong()
        else:
            AirValve.LowFlow()
        
    if (str(topic[-1]) == "bypass"):
        if (msg.payload == b'true'):
            AirValve.EnableByPassmode()
        else:
            AirValve.DisableByPassmode()

    if (str(topic[-1]) == "automode"):
        if (msg.payload == b'true'):
            AirValve.EnableAutomode()
        else:
            AirValve.DisableAutomode()
    
    if (str(topic[-1]) == "simulate"):
        controller.write_register(74,int(msg.payload))
    
    


instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 30)  # port name, slave address (in decimal)

instrument.serial.port     = '/dev/ttyUSB0'                 # this is the serial port name
instrument.serial.baudrate = 9600         # Baud
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 0.05          # seconds

instrument.address                         # this is the slave address number
instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
instrument.clear_buffers_before_each_transaction = True

controller = PSoC(30,instrument)
AirValve = Valve(30,instrument)

client = client = mqtt.Client()
client.connect("192.168.2.201", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

x = threading.Thread(target=client.loop_forever, args=())
x.start()

for i in range(1000000):
    controller.getRelais()
    Vac24 = 0
    if ((controller.Relais[0] & 1 ) == 0): Vac24 = 1
    AirValve1 = 0
    if ((controller.Relais[1] & 1 ) == 0): AirValve1 = 1
    AirValve2 = 0
    if ((controller.Relais[2] & 1 ) == 0): AirValve2 = 1
    HotWater = 0
    if ((controller.Relais[3] & 1 ) == 0): HotWater = 1
    HighFlow = 0
    if ((controller.Relais[4] & 1 ) == 0): HighFlow = 1
    HeatRequest = 0
    if ((controller.Relais[5] & 1 ) == 0): HeatRequest = 1

    client.publish("automation/climatronic/relais/vac24", Vac24)
    client.publish("automation/climatronic/relais/airvalve1", AirValve1)
    client.publish("automation/climatronic/relais/airvalve2", AirValve2)
    client.publish("automation/climatronic/relais/hotwater", HotWater)
    client.publish("automation/climatronic/relais/highflow", HighFlow)
    client.publish("automation/climatronic/relais/heatrequest", HeatRequest)
    
    
    controller.getTemperatures()
    client.publish("automation/climatronic/temperature/circulation",controller.Temperatures[0]/10)
    client.publish("automation/climatronic/temperature/extracted",controller.Temperatures[1]/10)
    client.publish("automation/climatronic/temperature/outside",controller.Temperatures[2]/10)
    client.publish("automation/climatronic/temperature/intake",controller.Temperatures[3]/10)
    

    controller.getHumidities()
    client.publish("automation/climatronic/humidity/circulation",controller.Humidities[0]/10)
    client.publish("automation/climatronic/humidity/extracted",controller.Humidities[1]/10)
    client.publish("automation/climatronic/humidity/outside",controller.Humidities[2]/10)
    client.publish("automation/climatronic/humidity/intake",controller.Humidities[3]/10)
    
    SysRegisters = controller.read_registers(12, 7)
    client.publish("automation/climatronic/temperature/cpu",SysRegisters[0])

    heater = (SysRegisters[1]) & 0xFF
    heaterstr = [ "CANCELED", "OFF", "REQUEST", "REQUESTED"]
    client.publish("automation/climatronic/heatingcontroller/statestr",heaterstr[heater])
    client.publish("automation/climatronic/heatingcontroller/state",heater)
    
    climate = (SysRegisters[1] >> 8) & 0xFF
    climatestr = ["RETURN_NORMAL", "NORMAL", "TO_HOT", "TO_COLD", "HIGH_TEMPERATURE_MODE", "LOW_TEMPERATURE_MODE"]
    client.publish("automation/climatronic/climatecontroller/state",climate)
    client.publish("automation/climatronic/climatecontroller/statestr",climatestr[climate])

    humidity = (SysRegisters[2] >> 8 ) & 0xFF
    humiditystr = ["CANCEL", "NORMAL", "OVERRIDE", "REQUEST_SHORT_OVERRIDE", "REQUEST_MEDIUM_OVERRIDE", "REQUEST_LONG_OVERRIDE", "REQUEST_OVERRIDE", "REQUEST_HIGHFLOW", "HIGH_FLOW"]
    client.publish("automation/climatronic/humiditycontroller/state",humidity)
    client.publish("automation/climatronic/humiditycontroller/statestr",humiditystr[humidity])
    
    controller.GetErrorWarning()
    client.publish("automation/climatronic/health/warning",controller.Warning)
    client.publish("automation/climatronic/health/error",controller.Error)

    print("Uptime: {} Error:{} Warning:{}".format(controller.getUptime(),controller.Error,controller.Warning))
    time.sleep(5)
#client.loop_forever()



# relais =  [1,1,1,1,1,1,1,1]
# for i in range(100):
#     print("Uptime: " + str(controller.getUptime()))
#     controller.getAdc_Values()
#     for adcVal in controller.AdcValues:
#         print("Adc: "+str(adcVal) + " mV")
    
#     relais_tmp = [1,1,1,1,1,1,1,1]

#     relais_tmp[1] = (controller.Uptime%2)
#     print(" {} - {}".format(relais,relais_tmp) )
    
#     if (relais != relais_tmp):
#         relais = relais_tmp
#         time.sleep(0.1)
#         print("ANDERS")
#         controller.Output_Push(relais_tmp)

#     time.sleep(0.1)
#     print(" ")

# controller.Relais(1,1)
# time.sleep(1)
# controller.Relais(1,0)
# time.sleep(1)
# controller.Relais(1,1)
# time.sleep(1)
# controller.Relais(1,0)
print("Uptime: " + str(controller.getUptime()))

client.loop_forever()

# ## Change temperature setpoint (SP) ##
# NEW_TEMPERATURE = 95
# instrument.write_regisiter(24, NEW_TEMPERATURE, 1)  # Registernumber, value, number of decimals for storage
