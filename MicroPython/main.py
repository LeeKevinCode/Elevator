import pyb
from pyb import UART
from pyb import Timer
cshort = bytearray(50)
clong = bytearray(500)
bs = 0
bf = 0
u1 = UART(1, 9600)
u1.writechar(250)
u1.writechar(4)
u1.writechar(5)
u1.writechar(1)
u1.writechar(252)
u1.writechar(128)
u1.writechar(6)
u1.writechar(3)
u1.writechar(119)
def callback1(timer):
	u1.readinto(cshort)
	print(cshort)
tim1 = Timer(1, freq = 1/3)
tim1.callback(callback1)

