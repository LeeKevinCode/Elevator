# main.py -- put your code here!
import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
clong = bytearray(1024)
lbel1 = 0
count = 0                          #For count every 30 sec

def getTime(u2):
    u2.writechar(26)
    u2.write('AT+CGSOCKCONT=1,"IP","sunsurf"\r')
    pyb.delay(1000)
    u2.write('AT+CHTTPACT="dataflow-1293.appspot.com",80\r')
    pyb.delay(8000)
    u2.write('GET /showTime HTTP/1.1\r\n')
    u2.write('Host:dataflow-1293.appspot.com\r\n')
    u2.write('Content-Length: 0\r\n')
    u2.writechar(10)
    u2.writechar(26)
    result = u2.readall()
    return str(result)

def initRTC(rtc, time):
    dt = eval(time)
    rtc.datetime(dt)

u1 = UART(1, baudrate=9600, read_buf_len=1024)
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

result = getTime(u2)
index = result.find("##")
while index == -1 or (index + 26) > len(result):
    result = getTime(u2)
    index = result.find("##")

rtc = pyb.RTC()
initRTC(rtc, result[index+2:index+26])

u1.writechar(128)
u1.writechar(6)
u1.writechar(3)
u1.writechar(119)

def mobileSig():
    laserSig = str(clong)
    length = len(laserSig)
    totalLength = length + 53
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
    u2.write('laserData=')
    u2.write(laserSig)
    u2.write('&rms=rms&rtc=rtc&temp=temp&cur=cur&hum=hum&')
    u2.writechar(26)
    pyb.delay(2000)
    print(u2.readall())
    print(rtc.datetime())

def laserDetecter(timer):
    global count, inputlength
    inputlength = u1.any()
    if 1024 < (inputlength + count):
        inputlength = 1024 - count
    for i in range(inputlength):
        clong[count + i] = u1.readchar()
    count = count + inputlength
    print(inputlength)
tim1 = Timer(3, freq = 1/2)
tim1.callback(laserDetecter)

def counter(timer):
    global lbel1
    lbel1 = 1
tim2 = Timer(4, freq = 1/30)
tim2.callback(counter)

while True:
    if lbel1 == 1:
        print(count)
        count = 0
        lbel1 = 0
        print(clong)
