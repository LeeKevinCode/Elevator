# main.py -- put your code here!
import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
rr = 15
countFinal = 30
cshort = bytearray(rr)
clong = bytearray(rr * countFinal)
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
lbel1 = 0
count1 = 0							#For count every 30 sec
def mobileSig():
	laserSig = str(clong)
	length = len(laserSig)
	totalLength = length + 18
	u2.writechar(26)
	u2.write('AT+CHTTPACT="dataflow-1293.appspot.com",80\r')
	pyb.delay(8000)
	u2.write('POST /test HTTP/1.1\r\n')
	u2.write('Host:dataflow-1293.appspot.com\r\n')
	u2.write('Content-Type:application/x-www-form-urlencoded\r\n')
	u2.write('Content-Length: ')
	u2.write(str(totalLength))
	u2.write('\r\n')
	u2.writechar(10)
	u2.write('name=')
	u2.write(laserSig)
	u2.write('&age=simcon1&')
	u2.writechar(26)
	pyb.delay(2000)
	print(u2.readall())

def laserDetecter(timer):
	global count1, rr, countFinal
	u1.readinto(cshort)
	for i in range(rr):
		clong[count1 * rr + i] = cshort[i]
		cshort[i] = 0
	count1 += 1
	if count1 >= countFinal:
		count1 = 0
	print(count1)
tim1 = Timer(3, freq = 1/2)
tim1.callback(laserDetecter)

def counter(timer):
	global lbel1
	lbel1 = 1
tim2 = Timer(4, freq = 1/30)
tim2.callback(counter)

while True:
	if lbel1 == 1:
		lbel1 = 0
		print('3G')
		mobileSig()



