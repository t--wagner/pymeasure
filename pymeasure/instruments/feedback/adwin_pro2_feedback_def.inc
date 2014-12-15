'<ADbasic Header, Headerversion 001.001>
'<Header End>
' ----- Detector ------
#Define detector 2
#Define detector_dword        Par_2
#Define detector_volt         FPar_2


' ----- Gate Channel ----- 
#Define gate 3
#Define gate_dword            Par_3
#Define gate_volt             FPar_3


' ----- Feedback -----
#Define feedback              1
#Define feedback_dword        Par_11
#Define feedback_volt         FPar_11
#Define feedback_next_volt    FPar_12
#Define feedback_next_dword   Par_12

#Define feedback_counts       Par_13
#Define feedback_rate         FPar_13
#Define feedback_factor       FPar_14
#Define feedback_status       Par_15

#Define range_low_volt        FPar_17
#Define range_low_dword       Par_17
#Define range_high_volt       FPar_18
#Define range_high_dword      Par_18


' ----- State boundaries -----
#Define state0_high_dword     Par_20
#Define state0_high_volt      FPar_20

#Define state0_low_dword      Par_21
#Define state0_low_volt       FPar_21

#Define state1_high_dword     Par_22
#Define state1_high_volt      FPar_22

#Define state1_low_dword      Par_23
#Define state1_low_volt       FPar_23

#Define window_time           FPar_25
#Define window                Par_25


' ----- Counter -----
#Define sample_nr             Par_26
#Define state                 Par_28

#Define counts0               Par_29
#Define counts1               Par_30

#Define counts0_nr            Par_31
#Define rate0                 FPar_31

#Define counts1_nr            Par_32
#Define rate1                 FPar_32

#Define length0               Par_33
#Define length1               Par_34
#Define length0_nr            Par_35
#Define length1_nr            Par_36

#Define sampling_rate         FPar_38
#Define com_rate              FPar_39

' ----- Update flags -----
#Define update                Par_41
#Define reset                 Par_42


' ----- Setter -----
#Define set_sampling_rate     FPar_44
#Define set_com_rate          FPar_45

#Define set_window_time       FPar_46

#Define set_state0_high_volt  FPar_48
#Define set_state0_low_volt   FPar_49
#Define set_state1_high_volt  FPar_50
#Define set_state1_low_volt   FPar_51

#Define set_range_low_volt    FPar_53
#Define set_range_high_volt   FPar_54

#Define set_feedback_rate     FPar_55
#Define set_feedback_factor   FPar_56
#Define set_feedback_status   Par_57

' ----- Fifo variables -----
#Define detector_fifo         Data_2
#Define gate_fifo             Data_3
#Define fifo_size 10000000
#Define detector_fifo_free    Par_60
#Define gate_fifo_free        Par_61

' ----- ADC values ------
#Define INTEGRATION_TIME      FPar_70 
#Define INTEGRATION_POINTS    Par_70
#Define TRIGGER               Par_71
#Define CONTINUOUS            Par_73

' ------ Module numbers ------
#Define adc_module 1
#Define dac_module 2

#Define dword_devider_18bit 131072
#Define bit_shift 6
#Define dword_devider_16bit 32768


' ------ Dword functions ------
Function dword16(value) As Float
  ' Tranform value to 16bit dword  
  dword16 = (value / 10 + 1) * 32768
EndFunction


Function dword18(value) As Float
  ' Transform value to 18bit dword
  dword18 = (value / 10 + 1) * 131072
EndFunction

