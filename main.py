import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
cshort = bytearray(40)
clong = bytearray(400)
bs = 0
bf = 0
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
	global bs, bf, count
	bs = u1.any()
	if bs > 0:
		u1.readinto(cshort)
		print(cshort)
	for i in range(bs):
		clong[bf + i] = cshort[i]
	bf += bs
	count ++
	if count >= 10:
		print(clong)
		count = 0
		bf = 0
tim1 = Timer(4, freq = 1/3)
tim1.callback(callback1)

