'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 3000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = Low
' Priority_Low_Level             = 1
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = THOMSON  FKP2\wagner
'<Header End>
' --- Communication Process ---- 

#Include ADwinPro_All.INC
#Include .\adwin_pro2_feedback_def.inc

Function fupdate() As Long:
  ' Update all parmeters
  
  ' ------ Communication rate ------
  If ((1 <= set_com_rate) and (set_com_rate <= 100)) Then
    com_rate = set_com_rate
    ProcessDelay = Round(300e6 / com_rate)
  EndIf
  
  ' ------ Sampling rate ------
  If ((100e3 <= set_sampling_rate) and (set_sampling_rate <= 500e3)) Then
    ' sampling_rate
    sampling_rate = set_sampling_rate
  EndIf
    
  ' ------ Window ------
  ' Calculate window length for time
  If (0 < set_window_time) Then
    window_time = set_window_time
    window = Round(window_time * sampling_rate)
  EndIf
  
    
  ' ------ Level boundaries ------ 
  ' Set voltage boundaries
  state0_high_volt = set_state0_high_volt
  state0_low_volt  = set_state0_low_volt
  state1_high_volt = set_state1_high_volt
  state1_low_volt  = set_state1_low_volt
    
  ' Calculate dword boundaries
  state0_high_dword = dword18(state0_high_volt)
  state0_low_dword  = dword18(state0_low_volt)
  state1_high_dword = dword18(state1_high_volt)
  state1_low_dword  = dword18(state1_low_volt)
  
  feedback_status = set_feedback_status
  feedback_factor = set_feedback_factor
  feedback_rate   = set_feedback_rate
  
  
  ' ------ Range ------    
  
  ' Hardware build in limits are (-10, 0)
  
  ' Set voltage ranges
  If ((-10 <= set_range_high_volt) And (set_range_high_volt <= 0)) Then
    range_high_volt = set_range_high_volt
  EndIf
  
  If ((-10 <= set_range_low_volt) And (set_range_low_volt <= 0)) Then
    range_low_volt  = set_range_low_volt
  EndIf
  
  ' Calculate corresponding dword range
  range_high_dword = dword16(range_high_volt)
  range_low_dword  = dword16(range_low_volt)
        
  ' ------ Reset ------
  ' Force reset of mainloop to handle all updates
  reset  = 1  
  
  ' Set back update flag
  fupdate = 0
EndFunction


Init:
  ' Load configuration script
  #Include .\adwin_pro2_feedback_conf.inc
  
  ' Initale update call
  update = fupdate()
  
Event:
  ' Handle update request
  if (update = 1) Then
    update = fupdate()
  EndIF
  
