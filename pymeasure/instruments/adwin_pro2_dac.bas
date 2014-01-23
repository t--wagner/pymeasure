'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = THOMSON  FKP2\wagner
'<Header End>
'------------------------------------------------------------------'
' Description:
' Control the DAC and ADC Cards. Always combine one DAC output and
' one ADC input as one channel. So you are able to readback the
' current output value. This allows you to reboot ADwin system 
' without out loosing the status of the DAC.
'
' Process number: 1
' 
' Global variables:
' Par_1 to Par_8
' FPar_1 to FPar_8
' Data_1[8] to store sampled data of all 8 Dac channels 
' Data_2[2] to communicate 
' -----------------------------------------------------------------


' Include all functions for the ADWinPro System
#Include ADwinPro_All.INC 

' Define the ADC and DAC module number
#Define adc_module 1
#Define dac_module 2

' Define sampling Rate
Dim sampling_rate As Long

' Store the current dac values in Data_1
Dim Data_9[8] As Long

' Communication via Data_2 field.
' Data_2[1] = dac_nr is the dac number. Data_2[1] = 0 means to do nothing.
' Data_2[2] = dac_val is value to set
Dim Data_10[2] As Long
#Define dac_nr Data_10[1]
#Define dac_val Data_10[2]

#Define fifo1_size 1000000
Dim Data_1[fifo1_size] As Float As Fifo
Dim Data_2[fifo1_size] As Float As Fifo
Dim Data_3[fifo1_size] As Float As Fifo
Dim Data_4[fifo1_size] As Float As Fifo
Dim Data_5[fifo1_size] As Float As Fifo
Dim Data_6[fifo1_size] As Float As Fifo
Dim Data_7[fifo1_size] As Float As Fifo
Dim Data_8[fifo1_size] As Float As Fifo

#Define dword_devider 13107.15
#Define bit_shift 6
' #Define adc_bit_devider 3276.75
' #Define adc_bit_shift 0 


Init:
  ' Set sampling-rate
  sampling_rate = 200e3
  ProcessDelay = 300e6 / sampling_rate
  
  ' Clear the request
  dac_nr = 0
  dac_val = -1
   
  ' Activate timer-modus for continous sampling
  P2_ADCF_Mode(adc_module, 1)
  
  '  Conversation on all Channels synchronous
  P2_Start_ConvF(1, 011111111b)  

  
Event:
  ' Read the 18bit values from all the ADC
  P2_Read_ADCF8_24B(adc_module, Data_9, 1)
  'P2_Read_ADCF8(adc_module, Data_9, 1)
  
  ' Set Dword and calculate the voltage value
  ' See the System and Hardware manual for information about the bit order.
  Par_1 = Shift_Right(Data_9[1], bit_shift)
  FPar_1 = (Par_1 / dword_devider) - 10
  Data_1 = FPar_1
    
  Par_2 = Shift_Right(Data_9[2], bit_shift)
  FPar_2 = (Par_2 / dword_devider) - 10
  Data_2 = FPar_2

  Par_3 = Shift_Right(Data_9[3], bit_shift)
  FPar_3 = (Par_3 / dword_devider) - 10
  Data_3 = FPar_3
  
  Par_4 = Shift_Right(Data_9[4], bit_shift)
  FPar_4 = (Par_4 / dword_devider) - 10
  Data_4 = FPar_4
  
  Par_5 = Shift_Right(Data_9[5], bit_shift)
  FPar_5 = (Par_5 / dword_devider) - 10
  Data_5 = FPar_5
  
  Par_6 = Shift_Right(Data_9[6], bit_shift)
  FPar_6 = (Par_6 / dword_devider) - 10
  Data_6 = FPar_6
  
  Par_7 = Shift_Right(Data_9[7], bit_shift)
  FPar_7 = (Par_7 / dword_devider) - 10
  Data_7 = FPar_7
  
  Par_8 = Shift_Right(Data_9[8], bit_shift)
  FPar_8 = (Par_8 / dword_devider) - 10
  Data_8 = FPar_8
  
  ' Check if a new transformation is requested.
  If ((dac_nr >= 1) And (dac_nr <= 8)) Then

    ' Check if the new setpoint is valid
    If ((dac_val >= 0) And (dac_val <= 65535)) Then
      P2_DAC(dac_module, dac_nr, dac_val)
    EndIf
    
    ' Clear the request
    dac_nr = 0
    dac_val = -1

  EndIf
