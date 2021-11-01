from io import UnsupportedOperation
import minimalmodbus
import serial
import time


class PSoC():

    DieTemperature_Offset = 9
    Clock_Offset = 36
    Uptime_Offset = 38
    Input_Offset = 57
    Output_Offset = 65
    DHT22Humidity_Offset = 40
    DHT22Temperature_Offset = 44
    AdcSamples_Offset = 48 
    AdcSlopes_Offset = 49
    AdcValues_Offset = 53
    Ventilation_Offset = 14
    Err_Wrng_Offset = 32


    # Values:
    Relais_Values = [0,0,0,0,0,0,0,0]
    Clock = 0
    Uptime = 0
    DieTemperature = 0
    AdcSlopes = [0,0,0,0]
    AdcSamples = 0
    AdcValues = [0,0,0,0]

    Temperatures = [0,0,0,0]
    Humidities = [0,0,0,0]
    Relais = [0,0,0,0,0,0,0,0]

    retryCount = 3   # number of retries
    retryDelay = 1 # in seconds

    waitAfterWrite = 0.075 # in seconds 50 mS

    def __init__(self, id, BusInstrument):
        self.instrument = BusInstrument
        self.id = id

    def read_Long(self, offset, signed=False):
        result  = 0
        error = 0
        for retry in range( 1, self.retryCount):
            try:
                result = self.instrument.read_long(offset,3, signed, minimalmodbus.BYTEORDER_LITTLE_SWAP) 
                return result
            except Exception as newError:
                error = newError
                time.sleep(self.retryDelay)
        raise error

    def read_register(self, offset, signed=False, decimals=0):
        result  = 0
        error = 0
        for retry in range( 1, self.retryCount):
            try:
                result = self.instrument.read_register(offset,decimals, 3, signed)
                return result
            except Exception as newError:
                error = newError
                time.sleep(self.retryDelay)
        raise error

    def read_registers(self, offset, number_of_registers):
        result = []
        error = 0
        for retry in range( 1, self.retryCount):
            try:
                result = self.instrument.read_registers(offset,number_of_registers, 3)
                return result
            except Exception as newError:
                error = newError
                time.sleep(self.retryDelay)
        raise error

    
    def write_registers(self, offset, values):
        result  = 0
        error = 0
        for retry in range( 1, self.retryCount):
            try:
                self.instrument.write_registers(offset, values)
                time.sleep(self.waitAfterWrite)
                return result
            except Exception as newError:
                error = newError
                print("Write_register failed - > retry" + str(retry))
                time.sleep(self.retryDelay)
        raise error

    def write_register(self, offset, value):
        result  = 0
        error = 0
        for retry in range( 1, self.retryCount):
            try:
                self.instrument.write_register(offset, value)
                time.sleep(self.waitAfterWrite)
                return result
            except Exception as newError:
                error = newError
                print("Write_register failed - > retry" + str(retry))
                time.sleep(self.retryDelay)
        raise error
    
    def TimedSetRelais(self, portId, state, CountDown):
        self.TimedRelais(portId, state, CountDown, 4)

    def TimedResetRelais(self, portId, state, CountDown):
        self.TimedRelais(portId, state, CountDown, 2)


    def TimedRelais(self, portId, state, CountDown, mode):
        if ( (portId > 8) | (portId < 0)  ):
            raise IndexError
        # as this is a relais with inverted output invert them
        if state == 1: 
            state = 0 
        else: 
            state = 1

        value = (CountDown<<8) | (mode) | state
        arr = [value]
        self.write_registers(self.Output_Offset + portId, arr)


    def Relais(self, portId, state):
        self.instrument.address = self.id
        print("Set Relais {} to {}".format(portId,state))
        # check if the port is in bound. of not raise exception
        if ( (portId > 8) | (portId < 0)  ):
            raise IndexError
        # as this is a relais with inverted output invert them
        if (state == 1) :
            self.Output_Values[portId] = 0
            state = [0]
        else:
            state = [1]
            self.Output_Values[portId] = 1

        self.write_registers(self.Output_Offset + portId, state)

    def Output_Push(self, Values=None):
        if ( Values != None ):
            self.Output_Values = Values
        self.write_registers(self.Output_Offset, self.Output_Values)

    def getUptime(self):
        self.Uptime = self.read_Long(self.Uptime_Offset)
        return self.Uptime

    def getAdc_Samples(self):
        self.AdcSamples = self.read_register(self.AdcSlopes_Offset)
        return self.AdcSamples

    def getAdc_Values(self):
        self.AdcValues = self.read_registers(self.AdcValues_Offset,4)
        return self.AdcValues

    def getAdc_Slopes(self):
        self.AdcSlopes = self.read_registers(self.AdcSlopes_Offset,4)
        return self.AdcSlopes
    
    def getTemperatures(self):
        self.Temperatures = self.read_registers(self.DHT22Temperature_Offset,4)
        return self.Temperatures

    def getHumidities(self):
        self.Humidities = self.read_registers(self.DHT22Humidity_Offset,4)
        return self.Humidities
    
    def getRelais(self):
        self.Relais = self.read_registers(self.Output_Offset, 8)
        return self.Relais

    def GetErrorWarning(self):
        ErrWrng = self.read_register(self.Err_Wrng_Offset)
        self.Error = ErrWrng & 0xFF
        self.Warning = ( ErrWrng >> 8 ) & 0xFF
        return ErrWrng
