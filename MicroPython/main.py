import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
rr = 15
countFinal = 30
cshort = bytearray(rr)
clong = bytearray(rr * countFinal)
ctest1 = bytearray(3)
ctest2 = bytearray(3)
count1 = 0
u1 = UART(1, 9600)
u2 = UART(2, baudrate=115200, read_buf_len=1024)
u2.writechar(26)
u2.write('AT+CGSOCKCONT=1,"IP","sunsurf"\r')
u1.writechar(128)
u1.writechar(6)
u1.writechar(2)
u1.writechar(120)
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
	global count1, rr, countFinal
	u1.readinto(cshort)
	for i in range(rr):
		clong[count1 * rr + i] = cshort[i]
		cshort[i] = 0
	count1 += 1
	if count1 >= countFinal:
		count1 = 0
tim1 = Timer(4, freq = 1)
tim1.callback(callback1)

def callback2(timer):
	count2 = 0
	u2.write('AT+CHTTPACT="dataflow-1293.appspot.com",80\r')
	u2.readinto(ctest1)
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
		if count2 > 500:
			count2 = 0
			u2.writechar(26)
			break
		ctest2[0] = ctest1[0]
		ctest2[1] = ctest1[1]
		ctest2[2] = ctest1[2]
	u2.write('POST /test HTTP/1.1\r\n')
	u2.write('Host:dataflow-1293.appspot.com\r\n')
	u2.write('Content-Type:application/x-www-form-urlencoded\r\n')
	u2.write('Content-Length: 23\r\n')
	u2.writechar(10)
	u2.write('name=test')
	u2.write(count2)
	u2.write('&age=simcon1&')
	u2.writechar(26)
tim2 = Timer(3, freq = 1/30)
tim2.callback(callback2)




