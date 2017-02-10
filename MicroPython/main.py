# main.py -- put your code here!
import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer

#################################################
####### All parameters ##########################
clong = bytearray(1024)
count = 0                          # For count data every 30 sec
lbel1 = 0                           # For every 30 sends out the data by 3G
lbel2 = 0                           # For every several hours to readjust the rtc time.
####### End parameters #########################

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


###### init device ###########################
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

###### End of init #######################

###### Send data  #######################
def mobileSig(count1):
    laserSig = str(clong[0:count1])
    rtcSig = str(rtc.datetime())
    totalData = 'laserData=' + laserSig + '&rms=rms&rtc=' + rtcSig + '&temp=temp&cur=cur&hum=hum&'
    totalLength = len(totalData)
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
    u2.write(totalData)
    u2.writechar(26)
    pyb.delay(2000)
    print(rtcSig)
    print(u2.readall())

######## laser distance data collection ###
def laserDetecter(timer):
    global count
    inputlength = u1.any()
    spacLabel = 0
    spacState = 1
    if 1024 < (inputlength + count):
        inputlength = 1024 - count
    for i in range(inputlength):
        c = u1.readchar()
        if (c >= 48 and c<=57) or c==46:
            spacLabel = 0
            clong[count] = c
            count += 1
            spacState = 0
        else:
            spacLabel = 1

        if spacLabel == 1 and spacState == 0:
            clong[count] = 32
            count += 1
            spacState = 1
    print(inputlength)
tim1 = Timer(3, freq = 1/2)
tim1.callback(laserDetecter)

######## Timer for send data ##############
def counter1(timer):
    global lbel1
    lbel1 = 1
tim2 = Timer(4, freq = 1/30)
tim2.callback(counter1)

######## Timer for adjust rtc #############
def counter2(timer):
    global lbel2
    lbel2 = 1
tim3 = Timer(5, freq = 1/3600)
tim3.callback(counter2)

while True:
    if lbel1 == 1:
        tempCount = count
        count = 0
        lbel1 = 0
        mobileSig(tempCount)
    if lbel2 == 1:
        lbel2 = 0
        result = getTime(u2)
        index = result.find("##")
        if index > -1 and (index + 26) < len(result):
            initRTC(rtc, result[index+2:index+26])
            rtcSig = str(rtc.datetime())
            print(rtcSig)


