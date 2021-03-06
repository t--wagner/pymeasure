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

' Constants
#Define pi             3.14159265359

' Module numbers
#Define adc_module                 2
#Define dac_module                 3

' Fifo variables
#Define fifo_size           10000000
#Define fifo_nr                    6

#Define adc_fifo              Data_1
#Define dac_fifo              Data_2
#Define digital_fifo          Data_3
#Define delta_fifo            Data_4
#Define time_fifo             Data_5
#Define count_fifo            Data_6

' Adc variables
#Define avg1_d                 Par_1 
#Define avg1_f                FPar_1 
#Define avg2_d                 Par_2 
#Define avg2_f                FPar_2 

' Dac variables
#Define dac1_next_f          FPar_11
#Define dac1_diff_next_d      Par_11
#Define dac2_next_f          FPar_12
#Define dac2_diff_next_d      Par_12
#Define dac3_next_f          FPar_13
#Define dac3_diff_next_d      Par_13
#Define dac4_next_f          FPar_14
#Define dac4_diff_next_d      Par_14

#Define dac1_d                Par_15
#Define dac1_f               FPar_15
#Define dac2_d                Par_16
#Define dac2_f               FPar_16
#Define dac3_d                Par_17
#Define dac3_f               FPar_17
#Define dac4_d                Par_18
#Define dac4_f               FPar_18


' State variables
#Define state                 Par_20
#Define time0                 Par_21
#Define time1                 Par_22

#Define state0_lower_lim_d    Par_23
#Define state0_lower_lim_f   FPar_23
#Define state0_upper_lim_d    Par_24
#Define state0_upper_lim_f   FPar_24

#Define state1_lower_lim_d    Par_25
#Define state1_lower_lim_f   FPar_25
#Define state1_upper_lim_d    Par_26
#Define state1_upper_lim_f   FPar_26  


' Feedback variables
#Define fb_status             Par_30
#Define fb_window_samples     Par_31
#Define fb_window            FPar_31
#Define fb_target_nr         FPar_32
#Define fb_target_rate       FPar_33
#Define fb_factor            FPar_34
#Define fb_factor_d           Par_34
#Define fb_samples            Par_35
#Define fb_counter0           Par_36
#Define fb_counts0            Par_37
#Define fb_counter1           Par_38
#Define fb_counts1            Par_39
#Define fb_delta             FPar_40
#Define fb_delta_sum         FPar_41
#Define fb_limit_low_f       FPar_42
#Define fb_limit_high_f      FPar_43
#Define start                 Par_44
#Define fb_error_low          Par_45
#Define fb_error_high         Par_46
#Define beating_freq         FPar_46
#Define step_ratio            Par_47
#Define oscillator_off       FPar_47
#Define oscillator_amp       FPar_48
#Define oscillator_freq      FPar_49


' Gate couplings
#Define c_tg4_m              FPar_50
#Define c_tg4_m_d             Par_50
#Define c_tg4_y              FPar_51
#Define c_tg4_y_d             Par_51
#Define c_tg3_m              FPar_52
#Define c_tg3_m_d             Par_52
#Define c_tg3_y              FPar_53
#Define c_tg3_y_d             Par_53
#Define c_qg1_m              FPar_54
#Define c_qg1_m_d             Par_54
#Define c_qg1_y              FPar_55
#Define c_qg1_y_d             Par_55

' Counting
#Define count_window_samples  Par_60
#Define count_window         FPar_60
#Define count_counter         Par_61
#Define count_counts          Par_62
#Define count_samples         Par_63

' Integration variables
#Define integration_points    Par_70
#Define integration_time     FPar_70 

#Define clear_fifo            Par_73
#Define reset_flag            Par_74















Dim sampling_rate             As Long

Dim state_flags               As Long

Dim adc_fifo    [fifo_size]   As Float As Fifo
Dim dac_fifo    [fifo_size]   As Float As Fifo
Dim digital_fifo[fifo_size]   As Long  As Fifo
Dim delta_fifo  [fifo_size]   As Float As Fifo
Dim time_fifo   [fifo_size]   As Long  As Fifo
Dim count_fifo  [fifo_size]   As Long  As Fifo

Dim adc1_d                    As Long
Dim adc2_d                    As Long

Dim avg_index                 As Long
Dim avg_adc1                  As Float
Dim avg_adc2                  As Float      

Dim time                      As Long
Dim i                         As Long

Dim oscillator_points         As Long
Dim oscillator_position       As Long
Dim oscillator_phase          As Float
Dim beating_points            As Long
Dim beating_position          As Long
Dim beating_phase             As Float

Dim limit_flag                As Long








































' Tranform value to 16bit dword
Function dword16(value) As Long
  dword16 = (value / 10 + 1) * 32768
EndFunction


'Transform 16bit dword to float value
Function float16(dword) As Float
  float16 = (dword / 32768 - 1) * 10
EndFunction


' Reset all variables
Function reset() as Long
  
  ' Set up feedback
  fb_status      = 0
  fb_samples     = 0
  fb_counts0     = 0
  fb_counts1     = 0
  fb_counter0    = 0
  fb_counter1    = 0
  fb_delta       = 0
  fb_delta_sum   = 0
  fb_error_low   = 0
  fb_error_high  = 0
  
  time  = 0
  time0 = 0
  time1 = 0
  
  count_counter = 0
  count_counts  = 0
  count_samples = 0
      
  
  For i = 1 To fifo_nr 
    FIFO_Clear(i)
  Next i
  
  If (start = 1) Then
    fb_status = 1
  EndIf
  
  reset = 0
EndFunction
















Init:
  
  ' Set sampling rate  
  sampling_rate = 400e3
  ProcessDelay = 1e9 / sampling_rate
  
  ' Set average filter
  P2_Set_Average_Filter(adc_module, 0)
  
  ' Continous sampling of ADC module
  P2_ADCF_Mode(Shift_Left(1, adc_module - 1), 1)
    
  ' Set up integration
  integration_time = 0.02
  integration_points = sampling_rate * integration_time 
  avg_index = 0
  avg_adc1 = 0
  avg_adc2 = 0
   
  reset_flag = reset()
  
  ' Init values for the feedback
  fb_window = 1e-3
  fb_target_nr = 3
  fb_factor = 4e-4 
  fb_limit_low_f = -0.860
  fb_limit_high_f = -0.760
  start = 0
  
  ' Some close by couplings
  c_tg4_m = -1.3107
  c_tg3_m =  0.975
  c_qg1_m = 0.14
  c_tg3_y = -0.37561726570129395
  c_tg4_y = -0.4439525306224823 
  c_qg1_y = -1.5295
  
  oscillator_off      = -0.810
  oscillator_amp      = 0.03
  oscillator_freq     = 8000
  beating_freq        = 4000
  oscillator_position = 0
  beating_position    = 0
  step_ratio          = 2
  
  count_window_samples = sampling_rate * 1e-3
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
Event:
  
  ' ##-------------------------------------##
  ' ##              Starting               ##
  ' ##-------------------------------------##
  
  ' Start feedback mode
  If (start = 1) Then
    reset_flag = reset()
    fb_status = 1
    start = 0
  EndIf
  
  ' Start normal counting mode
  If (start = 2) Then
    reset_flag = reset()
    fb_status = 2
    start = 0
  EndIf
  
  ' Start oscillator mode
  IF (start = 3) Then
    reset_flag = reset()
    fb_window = 1 / sampling_rate
    fb_status = 3
    start = 0
  Endif
  
  ' Start feedback testing mode
  If (start = 99) Then
    reset_flag = reset()
    fb_status = 99
    start = 0
  EndIf
  
    
  ' ##-------------------------------------##
  ' ##              ADC Input              ##
  ' ##-------------------------------------##
  
  adc1_d = P2_Read_ADCF(adc_module, 1)
  adc2_d = P2_Read_ADCF(adc_module, 2)
  
  adc_fifo = float16(adc2_d)
  
  ' ##-------------------------------------##
  ' ##               Average               ##
  ' ##-------------------------------------##
  Inc(avg_index)
  
  avg_adc1 = avg_adc1 + (adc1_d - avg_adc1) / avg_index    
  avg_adc2 = avg_adc2 + (adc2_d - avg_adc2) / avg_index

  If (avg_index >= integration_points) Then 
    avg1_d = avg_adc1
    avg2_d = avg_adc2
    
    avg1_f = float16(avg_adc1)
    avg2_f = float16(avg_adc2)
    
    avg_index = 0
    integration_points = sampling_rate * integration_time
  EndIf
    
  ' ##-------------------------------------##
  ' ##              Digitize             ##
  ' ##-------------------------------------##
  
  Inc(time)
  
  state0_lower_lim_d = dword16(state0_lower_lim_f)
  state0_upper_lim_d = dword16(state0_upper_lim_f)
  state1_lower_lim_d = dword16(state1_lower_lim_f)
  state1_upper_lim_d = dword16(state1_upper_lim_f)
  
  ' Check current state
  If (state = 0) Then
    
    ' Current sample in state 1
    If ((state1_lower_lim_d <= adc2_d) And (adc2_d <= state1_upper_lim_d)) Then
      
      time0 = time
      time_fifo = time0
      digital_fifo = 1
      
      time = 0
      state = 1
      Inc(fb_counter1)
      
    EndIf
    
  Else
    
    ' Current sample in state 0
    If ((state0_lower_lim_d <= adc2_d) And (adc2_d <= state0_upper_lim_d)) Then
      time1 = time
      time_fifo = time1
      digital_fifo = 0
      
      time = 0
      state = 0
      Inc(fb_counter0)
      Inc(count_counter)
    EndIf
    
  EndIf
    
  
  ' ##-------------------------------------##
  ' ##               Count                 ##
  ' ##-------------------------------------##
  
  Inc(count_samples)
  
  count_window_samples  = count_window * sampling_rate
  
  If (count_samples = count_window_samples) Then
    count_counts = count_counter
    count_fifo   = count_counter
    count_counter = 0
    count_samples = 0
  EndIf
  
  If ((count_samples > count_window_samples) Or (count_window_samples < 0)) Then
    count_counter = 0
    count_samples = 0
  EndIf 
  
  ' ##-------------------------------------##
  ' ##          Feedback protocol          ##
  ' ##-------------------------------------##
  
  ' Transform to dwords and back to get the real factor
  fb_window_samples = fb_window * sampling_rate
  fb_factor = fb_factor_d * 10 / 32768
  fb_target_rate = fb_target_nr / fb_window_samples * sampling_rate
  
  ' Increase feedback sample number
  Inc(fb_samples)
  
  ' Enter feedback modus (1) or testing mode (99)
  If (fb_status > 0) Then
    
    ' Feedback window end
    If (fb_samples = fb_window_samples) Then
      
      ' Set back feedback values
      fb_counts0   = fb_counter0
      fb_counts1   = fb_counter1
      
      fb_samples   = 0
      fb_counter0  = 0
      fb_counter1  = 0
      
      ' Calculate electron differences
      fb_delta     = fb_counts0 - fb_target_nr
      fb_delta_sum = fb_delta_sum + fb_delta
      
      ' Store the fifo data
      delta_fifo  = fb_delta
      dac_fifo    = float16(dac1_d)
      'dac_fifo    = float16(dac3_d)
      
      ' Apply feedback response
      If (fb_status = 1) Then 
        dac1_next_f = dac1_f + fb_factor * fb_delta                                       ' dg3
      EndIf
      
      
      ' Oscillator mode
      If (fb_status = 3) Then
        If (oscillator_freq > 0) Then
          oscillator_points = sampling_rate/oscillator_freq
          'beating_points    = sampling_rate/beating_freq
          
          If (oscillator_position = oscillator_points) Then
            oscillator_position = 0
          EndIf
          
          'If (beating_position = beating_points) Then
          '  beating_position = 0
          'EndIf
          
          oscillator_phase = 2 * pi * oscillator_position / oscillator_points
          'beating_phase    = 2 * pi * beating_position    / beating_points
          
          'dac1_next_f = oscillator_off + oscillator_amp * sin(oscillator_phase)
          
          dac3_next_f = c_tg3_y + oscillator_amp * sin(c_tg3_m * pi) * sin(oscillator_phase)  ' tg3
          dac2_next_f = c_tg4_y + oscillator_amp * cos(c_tg3_m * pi) * sin(oscillator_phase)  ' tg4
          
          
          'dac3_next_f = oscillator_off + oscillaotr_amp * sin(oscillator_phase)
          dac4_next_f =  -1.44 +  oscillator_amp * c_qg1_m  * sin(oscillator_phase)
          ' Beating
          ' dac1_next_f = oscillator_off + oscillator_amp * sin(oscillator_phase) * cos(beating_phase)
          
          ' Step function
          ' If (oscillator_position < oscillator_points / step_ratio) Then
          '  dac1_next_f = oscillator_off - oscillator_amp
          ' Else
          '   dac1_next_f = oscillator_off + oscillator_amp
          ' EndIF
          
          Inc(oscillator_position)
          Inc(beating_position)
        Else
          dac1_next_f = dac1_f
          dac2_next_f = dac2_f
          dac3_next_f = dac3_f
          dac4_next_f = dac4_f
        EndIf
        
      EndIf
      
      If (fb_status > 0) Then
        dac1_next_f = dac1_f
        'dac2_next_f = dac2_f
        'dac3_next_f = dac3_f
        'dac4_next_f = dac4_f
        
        ' Calculate coupled gate voltages
        'dac2_next_f =  dac1_next_f * c_tg4_m + c_tg4_y                                    ' tg4
        'dac3_next_f = (dac1_next_f * c_tg4_m + c_tg4_y) * c_tg3_m + c_tg3_y               ' tg3
        'dac4_next_f =  dac1_next_f * c_qg1_m + c_qg1_y                                    ' qg1
        'dac4_next_f =  dac1_next_f * c_qg1_m + c_qg1_y 

        ' Calculate the difference in dwords
        dac1_diff_next_d = dword16(dac1_next_f) - dac1_d
        dac2_diff_next_d = dword16(dac2_next_f) - dac2_d
        dac3_diff_next_d = dword16(dac3_next_f) - dac3_d
        dac4_diff_next_d = dword16(dac4_next_f) - dac4_d
      EndIf
      
    EndIf
    
    ' Reset the feedback if the samples somehow are to large or small (just for safty to avoid unexpected behaviour) 
    If ((fb_samples > fb_window_samples) Or (fb_samples < 0)) Then
      reset_flag = reset()
    EndIf  
    
    ' Check for low feedback boundary     
    If (fb_limit_low_f > dac1_next_f) Then
      
      dac1_next_f = dac1_f
      dac2_next_f = dac2_f
      dac3_next_f = dac3_f
      dac4_next_f = dac4_f
      
      Inc(fb_error_low)
    EndIf
    
    ' Check for high feedback boundary
    If (dac1_next_f > fb_limit_high_f) Then
      
      dac1_next_f = dac1_f
      dac2_next_f = dac2_f
      dac3_next_f = dac3_f
      dac4_next_f = dac4_f
      
      Inc(fb_error_high)
    EndIf
  EndIf    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
      
  ' ##-------------------------------------##
  ' ##             Dac Output              ##
  ' ##-------------------------------------##
  
  limit_flag = 0
  
  ' Check hardware limits of dac1
  If ((-1.0 <= dac1_next_f) And (dac1_next_f <= 0.16)) Then
    If ((-0.100 <= (dac1_next_f - dac1_f)) And ((dac1_next_f - dac1_f) <= 0.100)) Then
      Inc(limit_flag)
    EndIf
  EndIf
    
  ' Check hardware limits of dac2
  If ((-1.0 <= dac2_next_f) And (dac2_next_f <= 0.16)) Then
    If ((-0.100 < (dac2_next_f - dac2_f)) And ((dac2_next_f - dac2_f) < 0.100)) Then
      Inc(limit_flag)
    EndIf
  EndIf
      
  ' Check hardware limits of dac3
  If ((-1.0 <= dac3_next_f) And (dac3_next_f <= 0.16)) Then
    If ((-0.100 < (dac3_next_f - dac3_f)) And ((dac3_next_f - dac3_f) < 0.100)) Then
      Inc(limit_flag)
    EndIf
  EndIf
      
  ' Check hardware limits of dac4
  If ((-2.0 <= dac4_next_f) And (dac4_next_f <= 0.16)) Then
    If ((-0.100 < (dac4_next_f - dac4_f)) And ((dac4_next_f - dac4_f) < 0.100)) Then
      Inc(limit_flag)
    EndIf
  EndIf
  
  ' Only change the feedback voltage if all limits are fine
  If (limit_flag = 4) Then
    dac1_f = dac1_next_f
    dac1_d = dword16(dac1_next_f)
    dac2_f = dac2_next_f
    dac2_d = dword16(dac2_next_f)
    dac3_f = dac3_next_f
    dac3_d = dword16(dac3_next_f)
    dac4_f = dac4_next_f
    dac4_d = dword16(dac4_next_f)
  EndIf
  
    
  ' Set output registers
  P2_Write_DAC(dac_module, 1, dac1_d)
  P2_Write_DAC(dac_module, 2, dac2_d)
  P2_Write_DAC(dac_module, 3, dac3_d)
  P2_Write_DAC(dac_module, 4, dac4_d)
  P2_Start_DAC(dac_module)
    
    
  
  
  
  
  
  
  
  
  ' ##-------------------------------------##
  ' ##                Fifo                 ##
  ' ##-------------------------------------##
      
    
  'Par_75 = FIFO_Full(1)
  'Par_76 = FIFO_Full(2)
  'Par_77 = FIFO_Full(3)
  'Par_78 = FIFO_Full(4)
  'Par_79 = FIFO_Full(5)
  'Par_80 = FIFO_Full(6)
    
  ' ------ Reset ------
  If (reset_flag = 1) Then
    reset_flag = reset()
  EndIf
