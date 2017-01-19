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
u2 = UART(2, baudrate=115200, read_buf_len=1024)
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
u2.write('AT+CGSOCKCONT=1,"IP","sunsurf"\r')
pyb.delay(5000)
print(u2.readall())
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


ctest2[0] = ctest1[0]
ctest2[1] = ctest1[1]
ctest2[2] = ctest1[2]
while not (ctest2[0] == 82 and ctest2[1] == 69 and ctest2[2] == 81):
	u2.readinto(ctest1)
	count2 +=1
	if ctest2[1] == 82 and ctest2[2] == 69 and ctest1[0] == 81:
		break
	if ctest2[2] == 82 and ctest1[0] == 69 and ctest1[1] == 81:
		break
	if count2 > 5000:
		count2 = 0
		break
	ctest2[0] = ctest1[0]
	ctest2[1] = ctest1[1]
	ctest2[2] = ctest1[2]
	print(count2)

