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
u1 = UART(1, baudrate=115200, read_buf_len=1024)
u2 = UART(2, baudrate=115200, read_buf_len=1024)
u2.writechar(26)
u2.write('AT+CGSOCKCONT=1,"IP","sunsurf"\r')
u1.writechar(67)
pyb.delay(1000)

result = getTime(u2)
index = result.find("##")
while index == -1 or (index + 26) > len(result):
    result = getTime(u2)
    index = result.find("##")

rtc = pyb.RTC()
initRTC(rtc, result[index+2:index+26])
###### End of init #######################

###### Send data  #######################
def mobileSig(laserSig):
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
    inputlength += 1
    if myBufferLenght < (inputlength + count):
        inputlength = myBufferLenght - count
    for i in range(inputlength - 1):
        c = u1.readchar()
        if c < 10:
            clong[count] = c + 48
        elif c == 255:
            clong[count] = 32
        elif c == 10:
            clong[count] = 109          #error message
        else:
            count -= 1
        count += 1
    clong[count] = 110
    count += 1
tim1 = Timer(3, freq = 1)
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

def averageData(miniteData):
    countData = 0
    totalData = 0
    tempData = miniteData.split(' ')
    for i in range(len(tempData)):
        try:
            singleData = int(tempData[i])
            totalData += singleData
            countData += 1
        except:
            continue
    if countData == 0:
        return "error"
    else:
        return int(totalData/countData)

def parseLaserData(rawData):
    cookData = rawData.split('n')
    resultList = ' '
    for i in range(len(cookData) - 1):
        resultList += str(averageData(cookData[i])) + ' '
    return resultList

while True:
    if lbel1 == 1:
        tempCount = count
        count = 0
        lbel1 = 0
        mobileSig(parseLaserData(str(clong[0:tempCount])))
    if lbel2 == 1:
        lbel2 = 0
        result = getTime(u2)
        index = result.find("##")
        if index > -1 and (index + 26) < len(result):
            initRTC(rtc, result[index+2:index+26])
            rtcSig = str(rtc.datetime())
            print(rtcSig)


