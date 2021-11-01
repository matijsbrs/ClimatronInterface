import minimalmodbus
import serial
import time
from ModbusPSoC import PSoC

class Valve(PSoC):
    def __init__(self, id, BusInstrument):
        PSoC.__init__(self, id, BusInstrument)

    CountDown = 65
    ResetOnZero = 4
    SetOnZero = 2


    def OpenValve_1(self, id):
        Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0
        Relais_1 = (self.CountDown<<8) | (self.SetOnZero) | 1
        self.write_registers(self.Output_Offset + (id*2), [Relais_0, Relais_1])

        # self.TimedResetRelais(0,1,10)
        # self.TimedResetRelais(1,1,10)

        
    def CloseValve_2(self, id):
        Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0
        Relais_1 = (self.CountDown<<8) | (self.SetOnZero) | 0
        self.write_registers(self.Output_Offset + (id*2), [Relais_0, Relais_1])


    def Heating(self):
        Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0 # power relais
        Relais_1 = (self.CountDown<<8) | (self.SetOnZero) | 0 # Air Valve 1
        Relais_2 = (self.CountDown<<8) | (self.SetOnZero) | 0 # Air Valve 2
        Relais_3 = (self.CountDown<<8) | (self.SetOnZero) | 0 # Water Valve 
                    
        self.write_registers(self.Output_Offset, [Relais_0, Relais_1, Relais_2, Relais_3])

    def Normal(self):
        Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0 # power relais
        Relais_1 = (self.CountDown<<8) | (self.SetOnZero) | 1 # Air Valve 1
        Relais_2 = (self.CountDown<<8) | (self.SetOnZero) | 1 # Air Valve 2
        Relais_3 = (self.CountDown<<8) | (self.SetOnZero) | 1 # Water Valve 
        self.write_registers(self.Output_Offset, [Relais_0, Relais_1, Relais_2, Relais_3])
    
    def HighFlow(self):
        # Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0 # power relais
        # self.write_registers(self.Output_Offset , [Relais_0])
        Relais_4 = (self.CountDown<<8) | (self.SetOnZero) | 0 # power relais
        self.write_registers(self.Output_Offset + 4 , [Relais_4])

    def HighFlowShort(self):
        state = (3<<8) # short 
        self.write_registers( self.Ventilation_Offset, [state])
    
    def HighFlowMedium(self):
        state = (4<<8) # short 
        self.write_registers( self.Ventilation_Offset, [state])
    
    def HighFlowLong(self):
        state = (5<<8) # short 
        self.write_registers( self.Ventilation_Offset, [state])
    
    def EnableByPassmode(self):
        Relais_6 = 0 # power relais
        self.write_registers(self.Output_Offset+ 6, [Relais_6])

    def DisableByPassmode(self):
        Relais_6 = 1 # power relais
        self.write_registers(self.Output_Offset+ 6, [Relais_6])


    def LowFlow(self):
        # Relais_0 = (self.CountDown<<8) | (self.SetOnZero) | 0 # power relais
        # self.write_registers(self.Output_Offset , [Relais_0])
        state = (0<<8) # CANCEL high flow
        self.write_registers(self.Ventilation_Offset , [state])

    def EnableAutomode(self):
        self.write_register(18, 0x0700)
    
    def DisableAutomode(self):
        self.write_register(18, 0x0000)