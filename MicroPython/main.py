# main.py -- put your code here!
import micropython
micropython.alloc_emergency_exception_buf(100)
import pyb
from pyb import UART
from pyb import Timer
import os

#################################################
####### All parameters ##########################
myBufferLenght = 2000
clong = bytearray(myBufferLenght)
countLaser = 0                          # For count data every 30 sec
lbel1 = 0                           # For every 30 sends out the data by 3G
lbel2 = 0                           # For every several hours to readjust the rtc time.
fileNames = ['data0.txt','data1.txt','data2.txt','data3.txt',
'data4.txt','data5.txt','data6.txt','data7.txt','data8.txt','data9.txt']
## 10 data files
routine = '/sd/data/'               # data stored directory
fileSizeLimit = 2000                # each file size limit
recordAccSec = [-1] * 35            # record the starting point of data for each second 
recordAccCount = 0                  # record the second
currentFile = 0                     # set current data stored file
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
u2 = UART(2, baudrate=115200, read_buf_len=1024)
u3 = UART(3, baudrate=115200, read_buf_len=1024)
u4 = UART(4, baudrate=9600, read_buf_len=8096)
u6 = UART(6, baudrate=9600, read_buf_len=1024)
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
###### End of init #######################

###### Send data  #######################
def mobileSig(laserSig, rtcSig, accSig, others):
    totalData = 'laserData=' + laserSig + '&acc=' + accSig + '&rtc=' + rtcSig + '&temp=' + others[3] + '&cur1=' + others[0] + '&cur2=' + others[1] + '&hum=' + others[2] + '&'
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
    global countLaser
    inputlength = u3.any()
    inputlength += 1
    tempLabelN = 0
    if myBufferLenght < (inputlength + countLaser):
        inputlength = myBufferLenght - countLaser
    for i in range(inputlength - 1):
        c = u3.readchar()
        if c < 10:
            clong[countLaser] = c + 48
            countLaser += 1
        elif c == 255:
            clong[countLaser] = 32
            countLaser += 1
            if tempLabelN == 0:
                clong[countLaser] = 110
                countLaser += 1
                tempLabelN = 1
        elif c == 10:
            clong[countLaser] = 109          #error message
            countLaser += 1

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

######## Timer for Acc data collection ####
def accDetecter(timer):
    global recordAccCount
    inputlength = u4.any()
    recordAccSec[recordAccCount] = inputlength
    recordAccCount += 1
tim4 = Timer(6, freq = 1)
tim4.callback(accDetecter)

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

######## parse the laser data to a cloud recognised form #############
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

######## parse the ACC data to a cloud recognised form ##########
def parseAcc(rawData,startingRecord,recordNum):
    parseCount = 0
    result = ''
    if recordNum > 2:
        if startingRecord[0] > startingRecord[1]:
            startingRecord[0] = int (startingRecord[1] / 2)
    for i in range(recordNum):
        secondX = 0
        secondY = 0
        secondZ = 0
        countSec = 0
        while parseCount < startingRecord[i] - 10:
            if rawData[parseCount] == 85:
                parseCount +=1
                if rawData[parseCount] == 81:
                    parseCount +=1
                    x = rawData[parseCount] * 256 + rawData[parseCount+1]
                    y = rawData[parseCount+2] * 256 + rawData[parseCount+3]
                    z = rawData[parseCount+4] * 256 + rawData[parseCount+5]
                    parseCount +=5
                    secondX += x
                    secondY += y
                    secondZ += z
                    countSec += 1
                else:
                    parseCount -=1
            parseCount +=1
        if countSec == 0:
            result += 'error;'
        else:
            result += 'x:' + str(int(secondX/countSec)) + ' y:' + str(int(secondY/countSec)) + ' z:' + str(int(secondZ/countSec)) + ';'
    return result

################ parse other data ####################
def parseOthers(others):
    result0 = result1 = result2 =result3 = ''
    singles = others.split('\\r\\n')
    length = len(singles)
    for i in range(length):
        i0 = singles[i].find('Irms0')
        i1 = singles[i].find('Irms1')
        i2 = singles[i].find('Humidity')
        i3 = singles[i].find('Temperature')
        if i0 > -1 and i1 > -1 and i2 > -1 and i3 > -1:
            result0 += singles[i][i0+6:i1-1] + ';'
            result1 += singles[i][i1+6:i2-1] + ';'
            result2 += singles[i][i2+9:i3-1] + ';'
            result3 += singles[i][i3+12:] + ';'
    return [result0, result1,result2, result3]

################ Main Thread ####################
while True:
    if lbel1 == 1:
#################################################
        lbel1 = 0
        tempCount = countLaser
        countLaser = 0
#################################################
        recordNum = recordAccCount
        recordAccCount = 0
        temRecord = [-1] * recordNum
        temRecord[:] = recordAccSec[:recordNum]
#################################################
        otherCount = u6.any()
        others = u6.read(otherCount)
################ Laser parse ####################
        rawLaserData = str(clong[0:tempCount])
        cookedLaserData = parseLaserData(rawLaserData)
################ ACC parse ###################### 
        rawAcc = u4.read(temRecord[recordNum-1])
        cookedAccData = parseAcc(rawAcc, temRecord, recordNum)
################ Other parse ####################
        otherString = str(others)
        cookedOther = parseOthers(otherString)
        rtcSig = str(rtc.datetime())
        logData(rawLaserData+ ' ' + rtcSig + '\n')
        print(cookedOther[0] + '\n' + cookedLaserData + '\n' + cookedAccData + '\n' + rtcSig + '\n')
        mobileSig(cookedLaserData, rtcSig, cookedAccData, cookedOther)
    if lbel2 == 1:
        lbel2 = 0
        result = getTime(u2)
        index = result.find("##")
        print('index is' + str(index))
        if index > -1 and (index + 26) < len(result):
            initRTC(rtc, result[index+2:index+26])
            rtcSig = str(rtc.datetime())

