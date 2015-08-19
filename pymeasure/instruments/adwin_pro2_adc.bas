'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = THOMSON  FKP2\kuehne
'<Header End>
#Include ADwinPro_All.INC

' Define the ADC module number
#Define adc_module 1
#define adc_offset 8388608
#Define integration_time FPar_70 
#Define integration_points Par_70
#Define trigger Par_71
#Define continuous Par_72
#Define buffering Par_73
#Define buffered_points Par_74


' Event-loop frequency
Dim sampling_rate As Long

' Targets for channel readings
Dim adc_values[8] As Long

' Running average
Dim average1 As Float
Dim average2 As Float
Dim average3 As Float
Dim average4 As Float
Dim average5 As Float
Dim average6 As Float
Dim average7 As Float
Dim average8 As Float

' Averaging helper
Dim running_index As Long
Dim factor As Float

' Buffer
#Define fifo_size 100000
Dim Data_11[fifo_size] As Float As Fifo
#Define chan1_buffer Data_11
Dim Data_12[fifo_size] As Float As Fifo
#Define chan2_buffer Data_12
Dim Data_13[fifo_size] As Float As Fifo
#Define chan3_buffer Data_13
Dim Data_14[fifo_size] As Float As Fifo
#Define chan4_buffer Data_14
Dim Data_15[fifo_size] As Float As Fifo
#Define chan5_buffer Data_15
Dim Data_16[fifo_size] As Float As Fifo
#Define chan6_buffer Data_16
Dim Data_17[fifo_size] As Float As Fifo
#Define chan7_buffer Data_17
Dim Data_18[fifo_size] As Float As Fifo
#Define chan8_buffer Data_18

Init:
  ' Turn off trigger and buffer
  trigger = 0
  buffering = 0
  continuous = 1
  
  ' Counter for nr of points in buffer
  buffered_points = 0
  
  ' Set sampling rate  
  sampling_rate = 400e3
  integration_time = 0.02
  
  ' Calculate number of integration points
  ProcessDelay = 300e6 / sampling_rate
  integration_points = sampling_rate * integration_time
  
  ' Clear buffer and init FIFO-pointers
  FIFO_clear(11)
  FIFO_clear(12)
  FIFO_clear(13)
  FIFO_clear(14)
  FIFO_clear(15)
  FIFO_clear(16)
  FIFO_clear(17)
  FIFO_clear(18)
  
  ' Assign local variable values
  running_index = 1
    
  average1  = 0
  average2  = 0
  average3  = 0
  average4  = 0
  average5  = 0
  average6  = 0
  average7  = 0
  average8  = 0
  
  ' Activate timer-modus for continous sampling
  P2_ADCF_Mode(adc_module, 1)
    
  '  Conversation on all Channels synchronous
  P2_Start_ConvF(adc_module, 011111111b)
  
Event:
  P2_Read_ADCF8_24B(adc_module, adc_values, 1)  
  IF ((trigger = 1) OR (continuous = 1)) Then
             
    ' Running average
    factor = 1 - 1 / running_index
    average1 = average1 * factor + adc_values[1] / running_index
    average2 = average2 * factor + adc_values[2] / running_index
    average3 = average3 * factor + adc_values[3] / running_index
    average4 = average4 * factor + adc_values[4] / running_index
    average5 = average5 * factor + adc_values[5] / running_index
    average6 = average6 * factor + adc_values[6] / running_index
    average7 = average7 * factor + adc_values[7] / running_index
    average8 = average8 * factor + adc_values[8] / running_index       
       
    
    If (running_index >= INTEGRATION_POINTS) Then
      
      ' Put out the average channel value
      FPar_11 = (average1 / adc_offset - 1) * 10
      FPar_12 = (average2 / adc_offset - 1) * 10
      FPar_13 = (average3 / adc_offset - 1) * 10
      FPar_14 = (average4 / adc_offset - 1) * 10
      FPar_15 = (average5 / adc_offset - 1) * 10
      FPar_16 = (average6 / adc_offset - 1) * 10
      FPar_17 = (average7 / adc_offset - 1) * 10
      FPar_18 = (average8 / adc_offset - 1) * 10
      
      If (trigger = 1) Then
        
        ' Put averaged values in buffer
        chan1_buffer = FPar_11
        chan2_buffer = FPar_12
        chan3_buffer = FPar_13
        chan4_buffer = FPar_14
        chan5_buffer = FPar_15
        chan6_buffer = FPar_16
        chan7_buffer = FPar_17
        chan8_buffer = FPar_18
      
      EndIf
      
      ' Set back running_index
      running_index = 0
            
      average1  = 0
      average2  = 0
      average3  = 0
      average4  = 0
      average5  = 0
      average6  = 0
      average7  = 0
      average8  = 0
        
      ' Turn off trigger
      trigger = 0
               
    EndIf
      
    ' Increase the running index
    Inc(running_index)
  EndIf
    
  integration_points = sampling_rate * integration_time
