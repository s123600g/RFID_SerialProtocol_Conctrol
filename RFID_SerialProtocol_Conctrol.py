# -*- encoding: utf-8 -*-
'''
http://pyserial.readthedocs.io/en/latest/pyserial.html
http://zhangweide.cn/archive/2013/python-serial-package.html
https://blog.daychen.tw/2016/12/python-rs232.html
http://kunhsien.blogspot.com/2016/10/pythonpython-uartserial-i2c-spi-gpib.html
https://blog.csdn.net/dutsoft/article/details/79076327
'''
from __future__ import print_function

import serial
import serial.tools.list_ports
import time
import chardet
import sys
import binascii

# 運作模式(非測試模式 --> 0 , 測試模式 --> 1)
run_module = 1
# 測試模式下所要使用讀取模式(單一 --> 'r' , 多重 --> 'rs')
read_module = 'r'

'''---------------------------全域變數宣告--------------------------------------'''
# initialize Serial protocol
ser = serial.Serial()
# 讀取索引
read_index = 0


# 暫存結果
temp_list = list()

# 判斷RFID Reafer開啟關閉狀態
check_RF_status = "None"
''''--------------------------------------------------------------------------'''


# 控制RFID Reader輸出電源頻率
def control_RFID_Reader_OP(ser):

    # 判斷目前的RFID Reader是否處於連接狀態，如果是非處於連接狀態就執行連接動作
    if not ser._isOpen:
        # 開啟連接RFID Reader
        ser.open()

    # Write RF output power of reader
    ser.write('WP10')
    # print("設置Output Power: {}".format('17'))

    # 清除寫入的結果暫存(Read - - > input, Write - - > output)
    ser.flushOutput()

    # 關閉連接RFID Reader
    ser.close()


# 開起RFID Reader
def open_RFID_Reader(ser):

    global check_RF_status

    print("Serial Port isopen status: {}".format(ser._isOpen))

    # 判斷目前的RFID Reader是否處於連接狀態，如果是非處於連接狀態就執行連接動作
    if not ser._isOpen:
        # 開啟連接RFID Reader
        ser.open()

    # 開始RFID Reader讀取狀態
    ser.write('C')

    # 清除寫入的結果暫存(Read --> input , Write --> output)
    ser.flushOutput()

    # 關閉連接RFID Reader
    ser.close()

    # 設定check_RF_status參數值為"off"代表目前RFID Reader處於關閉狀態
    check_RF_status = "on"
    print("The RF on/off status: {}".format(check_RF_status))

    # 控制RFID Reader輸出電源頻率，控制頻率範圍
    control_RFID_Reader_OP(ser)


# 關閉RFID Reader
def close_RFID_Reader(ser):

    global check_RF_status

    print("Serial Port isopen status: {}".format(ser._isOpen))

    # 判斷目前的RFID Reader是否處於連接狀態，如果是非處於連接狀態就執行連接動作
    if not ser._isOpen:
        # 開啟連接RFID Reader
        ser.open()

    # 關閉RFID Reader讀取狀態
    ser.write('S')

    # 清除寫入的結果暫存(Read - - > input, Write - - > output)
    ser.flushOutput()

    # 關閉連接RFID Reader
    ser.close()

    # 設定check_RF_status參數值為"off"代表目前RFID Reader處於關閉狀態
    check_RF_status = "off"
    print("The RF on/off status: {}".format(check_RF_status))


# 初始化Serial Protocol 參數設定
def initialize_serial_argument(ser, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr):
    # 取得系統預設編碼型態
    reload(sys)

    '''初始化參數'''
    # System Usb Port , Windows name 'COM' ex: 'COM1' , Linux name '/dev/ttyUSB' ex: '/dev/ttyUSB0'
    ser.port = use_port
    # Device Baudrate
    ser.baudrate = baudrate
    # 讀取時間間隔 ,每一次讀取Tag間隔 , 如果是使用readline()不需要設定間隔,因為是以'\n'作為每次讀取的結束(斷點)
    ser.timeout = timeout
    # Tag 內容大小
    ser.bytesize = bytesize
    # 停止位
    ser.stopbits = stopbits
    # 軟體監控
    ser.rtscts = rtscts
    # 硬體監控
    ser.dsrdtr = dsrdtr

    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # print("System Default Encoding: '{}'".format(sys.getdefaultencoding()))
    # print("Use_Port: {}".format(use_port))
    # print("設備名稱: {}".format(ser.name))
    # print("波特率: {}".format(ser.baudrate))
    # print("校驗位: {}".format(ser.parity))
    # print("停止位: {}".format(ser.stopbits))
    # print("大小: {}".format(ser.bytesize))
    # print("軟件流控: {}".format(ser.rtscts))
    # print("硬件流控: {}".format(ser.dsrdtr))
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")


# 單一讀取模式
def read_module_readline(ser):

    global read_index

    # 讀取一行 , 以'\n'作為結束(斷點),要注意內容是否最後有'\n'最為結尾 , timeout設置為None
    response = ser.readline()

    # 判斷是否有讀取到Tag內容
    if len(response) is not 0:

        print('------------------------------------------------------')

        try:

            # 讀取索引 , 每一次讀取內容有值就+1,
            read_index += 1

            # 顯示輸出讀取結果
            print("No.{}\n\nRead RFID_Tag Value:\n\n十六進制: {} \n十進制: {}\n\nRFID_Tag Value Length: [ {} ]".format(
                read_index, response, int(response, 16), len(response)))

            print('------------------------------------------------------')

        except KeyboardInterrupt:

            print(KeyboardInterrupt.message)


# 多重讀取模式
def read_module_readlines(ser):

    global read_index

    temp_list = list()
    int_temp_list = list()

    # 讀取一行 , 以'\n'作為結束(斷點),要注意內容是否最後有'\n'最為結尾 , timeout設置為None
    response = ser.readlines()

    # 判斷是否有讀取到Tag內容
    if len(response) is not 0:

        print('------------------------------------------------------')

        try:

            # 讀取索引 , 每一次讀取內容有值就+1,
            read_index += 1

            # print("{}".format(response))

            for i in response:

                str_strip_temp = ''

                if i.rstrip('\r\n') not in temp_list:

                    str_strip_temp = i.rstrip('\r\n')
                    temp_list.append(str_strip_temp)
                    int_temp_list.append(int(str_strip_temp, 16))

            # print(temp_list)
            # print(int_temp_list)

            # # 顯示輸出讀取結果
            print("No.{}\n\nRead RFID_Tag Value:\n\n十六進制: {} \n十進制: {}\n\nRFID_Tag Value Number: [ {} ]".format(
                read_index, temp_list, int_temp_list, len(temp_list)))

            print('------------------------------------------------------')

        except KeyboardInterrupt:

            print(KeyboardInterrupt.message)


# 控制RFID
def star_RFID_control(read_module, sleep_time, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr):
    global temp_list
    global check_RF_status

    ser = serial.Serial()

    # '''執行初始化參數設定'''
    # initialize_serial_argument(ser)

    read_result = ""  # 儲存讀取的結果

    # 判斷所選擇的模式是否超出'r'或'rs'或'f',如果有就不執行判為錯誤模式
    if read_module != 'r' and read_module != 'rs' and read_module != 'f':

        print("read_module: {}".format(read_module))
        # isrunread = False
        print("讀取模式錯誤")

    elif read_module == 'f':

        # print("read_module: {}".format(read_module))

        # 先初始化設定RFID Reader 為關閉狀態,避免位在沒有要應用到RFID Reader頁面上一直感應嗶嗶叫

        # 如果要控制RFID Reader開關狀態,在軟件監控(rtscts)與硬件監控(dtscts)方面設定如下選擇
        # 1. 軟件監控(rtscts) --> False | 硬件監控(dtscts) --> False (最好用這一個)
        # 2. 軟件監控(rtscts) --> False | 硬件監控(dtscts) --> True (對readlines不能用)

        # ser = serial.Serial()

        # 不管是open還是connect都必須要先初始化才能做動作
        '''執行初始化參數設定'''
        initialize_serial_argument(
            ser, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr)

        # 開起RFID Reader
        # open_RFID_Reader(ser)

        if check_RF_status != "off":

            print("關閉RFID Reader避免一直感應嗶嗶叫.")

            # 關閉RFID Reader
            close_RFID_Reader(ser)

    elif read_module == 'r' or read_module == 'rs':

        # print("read_module: {}".format(read_module))

        # ser = serial.Serial()

        # 判斷讀取模式是否為'rs'
        if read_module == 'rs':

            # global check_initialize

            # # 判斷是否已經有先初始化過參數
            # if check_initialize == False:

            #     check_initialize = True

            #     # 如果是'rs'讀取模式,在serial timeout要設置指定秒數用來間隔每一次讀取時間
            #     DBM.RFIDReaderArgumentDB_update_timeout(1, 1)

            #     '''執行初始化參數設定'''
            #     initialize_serial_argument(ser)

            #     # 開起RFID Reader
            #     open_RFID_Reader(ser)

            read_result = list()  # 儲存讀取的結果

            # print("RFID讀取模式-->多重讀取模式")

            if check_RF_status != "on":

                # check_RF_status = "on"

                # 不管是open還是connect都必須要先初始化才能做動作
                '''執行初始化參數設定'''
                initialize_serial_argument(
                    ser, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr)

                # 開起RFID Reader
                open_RFID_Reader(ser)

            # 不管是open還是connect都必須要先初始化才能做動作
            '''執行初始化參數設定'''
            initialize_serial_argument(
                ser, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr)

            # 開啟連接RFID Reader
            ser.open()

            # # 開始自動循環掃描
            # while True:

            # 判斷RFID  Reader是否有正確開啟連接
            if ser._isOpen:

                # # 判斷讀取模式
                # if read_module == 'r':  # 單一讀取

                #     read_module_readline(ser)

                # elif read_module == 'rs':  # 多重讀取

                #     read_module_readlines(ser)

                # 進行多重讀取
                read_module_readlines(ser)

                # 如果判斷read_result長度不為0,代表有資料才顯示出內容
                if len(read_result) != 0:
                    print('------------------------------------------------------')
                    print("RFID read_result: \n{}".format(read_result))
                    print('------------------------------------------------------')

            else:

                print('RFID Reader連接關閉或非處於用到RFID頁面')
                # break

            # 清除每一次讀取的結果暫存(Read --> input , Write --> output)
            ser.flushInput()

            # # 每一次讀取程序完跟下一次讀取之間的間隔秒數 , 防止過於頻繁讀取導致出錯
            time.sleep(float(sleep_time))

            # 關閉連接RFID Reader
            ser.close()

        # 判斷讀取模式是否為'r'
        elif read_module == 'r':

            read_result = ""  # 儲存讀取的結果

            # print("RFID讀取模式-->單一讀取模式")

            # 不管是open還是connect都必須要先初始化才能做動作
            '''執行初始化參數設定'''
            initialize_serial_argument(
                ser, use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr)

            # 開起RFID Reader
            open_RFID_Reader(ser)

            # 開啟連接RFID Reader
            ser.open()

            # print(ser.is_open)

            if ser._isOpen:

                # 進行單一讀取
                read_module_readline(ser)

            else:

                print('RFID Reader連接關閉或非處於用到RFID頁面')

            # 清除每一次讀取的結果暫存(Read --> input , Write --> output)
            ser.flushInput()

            # 關閉連接RFID Reader
            ser.close()

            # # 關閉RFID Reader
            # close_RFID_Reader(ser)

        # 關閉RFID Reader
        close_RFID_Reader(ser)


'''測試模式下運行'''
if run_module == 1:

    print("\n")

    # 取得所有Port資訊
    port_list = list(serial.tools.list_ports.comports())

    # print(port_list[0][2])

    # 儲存可用的Port名稱
    use_port = ''

    # 掃描可用的Port名稱
    for port_item in port_list:

        # 判斷是否又抓到裝置名稱 , 如果有代表使用此port
        if port_item[2] != 'n/a':
            use_port = port_item[0]
            # print(port_item[0])

    if read_module == 'r':

        # read_module sleep_time use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr
        star_RFID_control('r', 0.15, use_port, 115200, None, serial.EIGHTBITS,
                          serial.STOPBITS_ONE, False, False)

    elif read_module == 'f':

        # read_module sleep_time use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr
        star_RFID_control('f', 0.0, use_port, 115200, None, serial.EIGHTBITS,
                          serial.STOPBITS_ONE, False, False)

    elif read_module == 'rs':

        # read_module sleep_time use_port, baudrate, timeout, bytesize, stopbits, rtscts, dsrdtr
        star_RFID_control('rs', 0.15, use_port, 115200, 1, serial.EIGHTBITS,
                          serial.STOPBITS_ONE, False, False)
