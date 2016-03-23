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

' Define sampling Rate
Dim sampling_rate As Long

' Define fifo size
#Define fifo_size 1000000

' Define the channel number to aquire from

#Define channel1 1
#Define channel1_par Par_1
#Define channel1_fpar FPar_1
Dim Data_1[fifo_size] As Long As Fifo
#Define channel1_fifo Data_1
#Define dword_devider 13107.15
#Define bit_shift 6

#Define channel2 2
#Define channel2_par Par_2
#Define channel2_fpar FPar_2
Dim Data_2[fifo_size] As Long As Fifo
#Define channel2_fifo Data_2

#Define dword_devider 13107.15
#Define bit_shift 6
' #Define dword_devider 3276.75
' #Define bit_shift 0

Init:
  ' Set sampling rate
  sampling_rate = 100e3
  ProcessDelay = 300e6 / sampling_rate
  
  ' Clear the fifo fields
  FIFO_Clear(channel1)
  FIFO_Clear(channel2)
  
  ' Activate timer-modus for continous sampling
  P2_ADCF_Mode(adc_module, 1)
  
  '  Conversation on all Channels synchronous
  P2_Start_ConvF(adc_module, 011111111b)
  
Event:

  ' Return the value
  channel1_par = Shift_Right(P2_Read_ADCF24(adc_module, channel1), bit_shift)
  channel1_fpar = channel1_par / dword_devider - 10
  channel1_fifo = channel1_par
  
  channel2_par = Shift_Right(P2_Read_ADCF24(adc_module, channel2), bit_shift)
  channel2_fpar = channel2_par / dword_devider - 10
  channel2_fifo = channel2_par
  
  ' Check the
  Par_20 = FIFO_Full(channel1)
  Par_21 = FIFO_Full(channel2)
  
