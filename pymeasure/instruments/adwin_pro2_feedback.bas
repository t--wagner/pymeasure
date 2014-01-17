'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
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
#Include ADwinPro_All.INC

' Define the ADC and DAC module number
#Define adc_module 1
#Define dac_module 2

' Define sampling Rate
Dim sampling_rate As Long

#Define bitsize 18
Dim dword_devider As Float
Dim bit_shift As Long

#Define state1_low  135300
#Define state1_high 135500
#Define state2_low  134650
#Define state2_high 134850

' Define fifo size
#Define fifo1_size 1000000

' Define the sighnal input channel
#Define input 8
#Define input_par Par_8
#Define input_fpar FPar_8
Dim Data_8[fifo1_size] As Long As Fifo
#Define input_fifo Data_8





Dim last_state As Long



Init:  
  ' Set sampling rate
  sampling_rate = 10e3
  ProcessDelay = 300e6 / sampling_rate
  
  last_state = 1

  If(bitsize = 18) Then
    dword_devider = 13107.15
    bit_shift = 6
  Else
    dword_devider = 3276.75
    bit_shift = 0
  EndIf
  
  ' Clear the fifo fields
  FIFO_Clear(input)
  
  ' Activate timer-modus for continous sampling
  P2_ADCF_Mode(adc_module, 1)
  
  '  Conversation on all Channels synchronous
  P2_Start_ConvF(adc_module, 00000001b)
  
  par_11 = 0
  par_12 = 0
  
Event:
  input_par = Shift_Right(P2_Read_ADCF24(adc_module, input), bit_shift)
  
  If(last_state = 1) Then
    If((input_par >= state1_low) And (input_par <= state1_high)) Then
      Inc(Par_11)     
      last_state = 2
      P2_DAC(dac_module, 1, 31278)
      
    EndIF
  Else
    If((input_par >= state2_low) And (input_par <= state2_high)) Then
      Inc(Par_12)
      last_state = 1
      P2_DAC(dac_module, 1, 31279)
    EndIf
  EndIF
  
      
  
  input_fifo = input_par
  
  ' Check the
  Par_21 = FIFO_Full(input)
