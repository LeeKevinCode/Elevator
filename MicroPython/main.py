import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
rr = 15
countFinal = 30
cshort = bytearray(rr)
clong = bytearray(rr * countFinal)
count = 0
u1 = UART(1, 9600)
u1.writechar(250)
u1.writechar(4)
u1.writechar(5)
u1.writechar(1)
u1.writechar(252)
pyb.delay(1000)
u1.writechar(128)
u1.writechar(6)
u1.writechar(3)
u1.writechar(119)
def callback1(timer):
	global count, rr
	u1.readinto(cshort)
	for i in range(rr):
		clong[count * rr + i] = cshort[i]
		cshort[i] = 0
	count += 1
	if count >= countFinal:
		print(clong)
		count = 0
tim1 = Timer(4, freq = 1)
tim1.callback(callback1)

