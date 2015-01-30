'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
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
#Include .\adwin_pro2_feedback_def.inc

' Variables to store adc values
Dim adc_values[8] As Long 

Dim detector_fifo[fifo_size] As Float As Fifo
Dim gate_fifo[fifo_size] As Float As Fifo

Dim dword16_buf as Long

Function freset() As Long
  ' Reset all analysis values
  
  ' Savly change the ProcessDelay
  ProcessDelay = Round(300e6 / sampling_rate) 
  
  ' Clear the fifos
  FIFO_Clear(detector)
  FIFO_Clear(gate)
    
  ' Clear all state and counting informations
  state      = -1
  sample_nr  =  0
  counts0    =  0
  counts1    =  0
  counts0_nr =  0
  counts1_nr =  0
  rate0      =  0
  rate1      =  0
  length0    =  0
  length1    =  0
  length0_nr =  0
  length1_nr =  0
  
  ' Reset flag back to False
  freset = 0
EndFunction

Function feedback_function() As Float
  feedback_function = feedback_volt + feedback_factor * (rate0 - feedback_rate)
EndFunction


Init:
  
  
  reset = freset()
  
  ' Activate timer-modus for continous sampling and synchronous conversation
  P2_ADCF_Mode(adc_module, 1)
  P2_Start_ConvF(adc_module, 011111111b)
  
Event:
  ' ------ Aquire ADC Channels ------
  P2_Read_ADCF4_24B(adc_module, adc_values, 1)
  
  ' Sample detector
  detector_dword = Shift_Right(adc_values[2], bit_shift)
  detector_volt = 10 * (detector_dword / dword_devider_18bit - 1)
  detector_fifo = detector_volt
      
  ' Sample gate
  gate_dword = Shift_Right(adc_values[3], bit_shift)
  gate_volt = 10 * (gate_dword / dword_devider_18bit - 1)
  gate_fifo = gate_volt
  
  Inc(sample_nr)
  
  ' ------ Reset ------
  If (reset = 1) Then
    reset = freset()
  EndIf
  
  
  ' ------ Detect Levels ------
  ' Level 0
  If((state = 0) or (state = -1)) Then
    If ((state1_low_volt <= detector_volt) And (detector_volt <= state1_high_volt)) Then
      Inc(counts0)
      state = 1
      length0_nr = length0
      length1 = 1
    Else
      Inc(length0)   
    EndIF
  Else
    ' Level 1
    If((state = 1) or (state = -1)) Then
      If((state0_low_volt <= detector_volt) And (detector_volt <= state0_high_volt)) Then
        ' Increase counts in window
        Inc(counts1)
              
        ' Update level 1 length
        length1_nr = length1
        
        ' Toggle state
        state = 0
        
        ' Length 0 state 
        length0 = 1
      Else
        Inc(length1)
      EndIf
    EndIf
  EndIf
  
  
  ' ------ Window ------
  If (sample_nr = window) Then
       
    sample_nr  = 0
       
    counts0_nr = counts0
    rate0      = counts0 / window_time
    counts0    = 0
    
    counts1_nr = counts1
    rate1      = counts1 / window_time
    counts1    = 0
    
    ' Handle feedback
    feedback_next_volt = feedback_function()
    feedback_next_dword = dword16(feedback_next_volt)
  Else
    ' Some saty to make sure
    If (sample_nr > window) Then
      reset = 1
    EndIF
  EndIf
  
  
  ' ------ FIFO ------
  detector_fifo_free = FIFO_Empty(detector)
  gate_fifo_free     = FIFO_Empty(gate)
  
  
  ' ------ Dac Output ------
  If (feedback_status = 1) Then
    feedback_volt = feedback_next_volt
    dword16_buf   = feedback_next_dword
  Else:
    dword16_buf = dword16(feedback_volt)
  EndIf
  
  ' Check range limits
  If ((range_low_dword <= dword16_buf) and (dword16_buf <= range_high_dword)) Then
    ' Value in range
    feedback_dword = dword16_buf  
    ' Set dac output value
    P2_DAC(dac_module, feedback, feedback_dword)
  Else
    If (dword16_buf <= range_low_dword) Then
      ' Value to low
      feedback_volt = range_low_volt
      feedback_dword = range_low_dword
      P2_DAC(dac_module, feedback, feedback_dword)
    Else
      If (dword16_buf >= range_high_dword) Then
        ' Value to high
        feedback_volt = range_high_volt
        feedback_dword = range_high_dword
        P2_DAC(dac_module, feedback, feedback_dword)
      EndIf
    EndIf
  EndIf
    

  
