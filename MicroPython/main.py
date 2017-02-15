# main.py -- put your code here!
import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
import os

#################################################
####### All parameters ##########################
myBufferLenght = 2500
clong = bytearray(myBufferLenght)
count = 0                          # For count data every 30 sec
lbel1 = 0                           # For every 30 sends out the data by 3G
lbel2 = 0                           # For every several hours to readjust the rtc time.
fileNames = ['data0.txt','data1.txt','data2.txt','data3.txt',
'data4.txt','data5.txt','data6.txt','data7.txt','data8.txt','data9.txt']
## 10 data files
routine = '/sd/data/'               # data stored directory
fileSizeLimit = 2000                # each file size limit
####### End parameters #########################

###### get current time from cloud ###########################
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

###### init rtc ###########################
def initRTC(rtc, time):
    dt = eval(time)
    rtc.datetime(dt)

###### init device ###########################
u3 = UART(3, baudrate=115200, read_buf_len=1024)
u2 = UART(2, baudrate=115200, read_buf_len=1024)
u2.writechar(26)
u2.write('AT+CGSOCKCONT=1,"IP","sunsurf"\r')
# set simcard apn
pyb.delay(1000)

result = getTime(u2)
index = result.find("##")
while index == -1 or (index + 26) > len(result):
    result = getTime(u2)
    index = result.find("##")

rtc = pyb.RTC()
initRTC(rtc, result[index+2:index+26])
u3.writechar(67)
os.chdir('/sd/data')
currentFile = 0                 # set current data stored file
###### End of init #######################

###### Send data  #######################
def mobileSig(laserSig, rtcSig):
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
    print(u2.readall())

######## laser distance data collection ###
def laserDetecter(timer):
    global count
    inputlength = u3.any()
    inputlength += 1
    tempLabelN = 0
    if myBufferLenght < (inputlength + count):
        inputlength = myBufferLenght - count
    for i in range(inputlength - 1):
        c = u3.readchar()
        if c < 10:
            clong[count] = c + 48
            count += 1
        elif c == 255:
            clong[count] = 32
            count += 1
            if tempLabelN == 0:
                clong[count] = 110
                count += 1
                tempLabelN = 1
        elif c == 10:
            clong[count] = 109          #error message
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

######## Average the per second data #############
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

######## parse the data to a cloud recognised form #############
def parseLaserData(rawData):
    cookData = rawData.split('n')
    resultList = ''
    for i in range(1, len(cookData)):
        resultList += str(averageData(cookData[i])) + ' '
    resultList = resultList[:-1]
    return resultList

######## get current data file size #############
def getSizeOfFile(fileName):
    try:
        state = os.stat(routine+fileName)
        return int(state[6])
    except:
        return -1

######## log raw data to data files on sd card #############
def logData(rawData):
    global currentFile
    size = getSizeOfFile(fileNames[currentFile])
    if size > fileSizeLimit or size == -1:
        if size > fileSizeLimit:
            currentFile += 1
            currentFile %= 10
        tempF = open(fileNames[currentFile], 'w')
        tempF.write("### Start of Data ###\n\n")
        tempF.close()
    file = open(fileNames[currentFile], 'a')
    file.write(rawData)
    file.close()

while True:
    if lbel1 == 1:
        tempCount = count
        count = 0
        lbel1 = 0
        rawData = str(clong[0:tempCount])
        cookedData = parseLaserData(rawData)
        rtcSig = str(rtc.datetime())
        logData(rawData+ ' ' + rtcSig + '\n')
        # print(cookedData+ ' ' + rtcSig + '\n')
        mobileSig(cookedData, rtcSig)
    if lbel2 == 1:
        lbel2 = 0
        result = getTime(u2)
        index = result.find("##")
        print('index is' + str(index))
        if index > -1 and (index + 26) < len(result):
            initRTC(rtc, result[index+2:index+26])
            rtcSig = str(rtc.datetime())

