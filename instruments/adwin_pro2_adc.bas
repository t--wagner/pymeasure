'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 2000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.0.0
' Optimize                       = Yes
' Optimize_Level                 = 4
' Stacksize                      = 1000
' Info_Last_Save                 = THOMSON  FKP2\wagner
'<Header End>
#Include ADwinPro_All.INC

' Define the ADC module number
#Define adc_module 2
#define adc_offset 32767.5
#Define integration_time FPar_70 
#Define integration_points Par_70
#Define output Data_22

' Event-loop frequency
Dim sampling_rate As Long

' Targets for channel readings
Dim adc_values[8] As Long
Dim average[8] As Float
Dim output[8] As Float

' Averaging helper
Dim average_index As Long

Dim i As Long

Init:
  
  ' Set sampling rate  
  sampling_rate = 500e3
  integration_time = 0.02
  
  ' Calculate number of integration points
  ProcessDelay = 2000
  integration_points = sampling_rate * integration_time
  
 
  ' Assign local variable values
  average_index = 0
  For i = 1 To 8:
    average[i] = 0 
  Next i
  
  
  'P2_Burst_Init(adc_module, 1, 0, 8, 0, 010b)
  P2_ADCF_Mode(110b, 0)
  'P2_Set_Average_Filter(adc_module, 3)
Event:
  Inc(average_index)
  
  P2_Read_ADCF8(adc_module, adc_values, 1)
  
  ' Running average
  For i = 1 To 8:
    average[i] =  average[i] + (adc_values[i] - average[i]) / average_index    
  Next i

  If (average_index >= integration_points) Then
      
    For i = 1 To 8:
      output[i] = (average[i] / adc_offset - 1) * 10 
    Next i
    
    FPar_11 = output[1]
    FPar_12 = output[2] 
    FPar_13 = output[3]
    FPar_14 = output[4]
    FPar_15 = output[5]
    FPar_16 = output[6]
    FPar_17 = output[7]
    FPar_18 = output[8]

    average_index = 0
    integration_points = sampling_rate * integration_time
   
  EndIf
  
  
