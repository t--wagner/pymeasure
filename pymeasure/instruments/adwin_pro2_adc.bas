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
#Define ADC_MODULE 1
#define ADC_OFFSET 8388608
#Define INTEGRATION_TIME FPar_1 
#Define INTEGRATION_POINTS Par_1 

Dim running_index As Long
Dim factor As Float
 
Dim adc_values[8] As Long
Dim sampling_rate As Long

Dim average1 As Float
Dim average2 As Float
Dim average3 As Float
Dim average4 As Float
Dim average5 As Float
Dim average6 As Float
Dim average7 As Float
Dim average8 As Float



Init:
  ' Set sampling rate  
  sampling_rate = 400e3
  INTEGRATION_TIME = 0.02
  
  ProcessDelay = 300e6 / sampling_rate
  INTEGRATION_POINTS = sampling_rate * INTEGRATION_TIME
  
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
  P2_Read_ADCF8_24B(ADC_MODULE, adc_values, 1)  
  
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
    FPar_11 = (average1 / ADC_OFFSET - 1) * 10
    FPar_12 = (average2 / ADC_OFFSET - 1) * 10
    FPar_13 = (average3 / ADC_OFFSET - 1) * 10
    FPar_14 = (average4 / ADC_OFFSET - 1) * 10
    FPar_15 = (average5 / ADC_OFFSET - 1) * 10
    FPar_16 = (average6 / ADC_OFFSET - 1) * 10
    FPar_17 = (average7 / ADC_OFFSET - 1) * 10
    FPar_18 = (average8 / ADC_OFFSET - 1) * 10
  
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
      
  EndIf
  
  ' Increase the running index
  Inc(running_index)
  
  'integration_points = 300e6  / ProcessDelay *  integration_time