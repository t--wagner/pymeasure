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
' Info_Last_Save                 = ORWELL  FKP2\bayer
'<Header End>
#Include ADwinPro_All.INC

' Define the ADC module number
#Define adc_module 1
#Define trigger Par_2


' Define sampling Rate
Dim sampling_rate As Long

#Define integration_time FPar_1 
#Define integration_points Par_1 

Dim running_index As Long
 
Dim adc_values[8] As Long
Dim sum[8] As Long
Dim i As Long
Dim voltages[8] As Long
Dim val As Long


#Define dword_devider 13107.15
#Define bit_shift 6

Init:
  ' Set sampling rate  
  integration_time = 0.02
  
  
  ProcessDelay = 300e6 / 500e3
  integration_points = 500e3 * integration_time
  
  
  running_index = 1
  
  ' Activate timer-modus for continous sampling
  P2_ADCF_Mode(adc_module, 1)
    
  '  Conversation on all Channels synchronous
  P2_Start_ConvF(adc_module, 011111111b)
  
Event:
  P2_Read_ADCF8_24B(adc_module, adc_values, 1)  
  

  Par_11 = Par_11  + Shift_Right(adc_values[1], 6)
  Par_12 = Par_12  + Shift_Right(adc_values[2], 6)
  Par_13 = Par_13  + Shift_Right(adc_values[3], 6)
  Par_14 = Par_14  + Shift_Right(adc_values[4], 6)
  Par_15 = Par_15  + Shift_Right(adc_values[5], 6)
  Par_16 = Par_16  + Shift_Right(adc_values[6], 6)
  Par_17 = Par_17  + Shift_Right(adc_values[7], 6)
  Par_18 = Par_18  + Shift_Right(adc_values[8], 6)

  If (running_index >= integration_points) Then
    
    ' Put out the average channel value
    FPar_11 = Par_11 / integration_points / dword_devider - 10
    FPar_12 = Par_12 / integration_points / dword_devider - 10
    FPar_13 = Par_13 / integration_points / dword_devider - 10
    FPar_14 = Par_14 / integration_points / dword_devider - 10
    FPar_15 = Par_15 / integration_points / dword_devider - 10
    FPar_16 = Par_16 / integration_points / dword_devider - 10
    FPar_17 = Par_17 / integration_points / dword_devider - 10
    FPar_18 = Par_18 / integration_points / dword_devider - 10
    
    ' Set back running_index
    running_index = 0
        
    Par_11 = 0
    Par_12 = 0
    Par_13 = 0
    Par_14 = 0
    Par_15 = 0
    Par_16 = 0
    Par_17 = 0
    Par_18 = 0
    
  EndIf
  
  ' Increase the running index
  Inc(running_index)
  
  integration_points = 300e6  / ProcessDelay *  integration_time
