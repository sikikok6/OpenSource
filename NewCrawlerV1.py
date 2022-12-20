import time
import requests
import pandas as pd




def getbusinfo(head,tail,bus_num,bus_dir):
    cookies = {}

    headers = {
        'token': head + time.strftime('%H%M') + tail,
    }

    data = {
        'action': 'dy',
        'routeName': bus_num,
        'dir': bus_dir,
        'lang': 'zh-tw',
        'device': 'web'
    }

    response = requests.post('https://bis.dsat.gov.mo:37812/macauweb/routestation/bus', headers=headers,
                             cookies=cookies, data=data)

    return response.json()

def generate_info(busdata):
    InfoList = []
######REVERSED HERE#####
    for i in reversed(range(len(busdata))):
        staInfo = busdata[i]
        staCode = staInfo['staCode']

        for j in range(len(staInfo['busInfo'])):
            busInfo = staInfo['busInfo'][j]

            busPlate = busInfo['busPlate']
            status = busInfo['status']

            dic_key = ['busPlate','status','staCode']
            dic_value = [busPlate,status,staCode]
            dic_info = dict(zip(dic_key,dic_value))
            print(dic_info)
            InfoList.append(dic_info)
    return InfoList

##巴士列表中是否出现过这辆车,并根据此生成新车牌号
def CheckAndGenBusPlate(RawBusPlate):
    if (RawBusPlate not in Bus_Dic):
        Bus_Dic[RawBusPlate] = 0

    return RawBusPlate + '-' + str(Bus_Dic[RawBusPlate])

##是否需要向时刻表中添加车牌作为索引
def CheckAddTable(busPlate):
    if(busPlate not in tableInfo['Bus'].values):
        NewAdd=[busPlate]
        for _ in range(len(colName)-1):
            NewAdd.append("")
        rowNum = tableInfo.shape[0]
        tableInfo.loc[rowNum] = NewAdd

def UpdateBusPlate(NewBusPlate):
    RawBusPlate = NewBusPlate[:6]
    Bus_Dic[RawBusPlate] += 1


def Main_Crawler():


    head = "53b920227eca2902122042d0728abde7"
    tail = "b7d99927"
    bus_num = "51"
    bus_dir = "0"

    busdata_txt = getbusinfo(head, tail, bus_num, bus_dir)
    busdata = busdata_txt['data']['routeInfo']
    InfoList = generate_info(busdata)

    ####!!!STALIST!!!!
    staList = []
    for i in range(len(busdata)):
        staInfo = busdata[i]
        staCode = staInfo['staCode']
        staList.append(staCode)
    global colName
    colName = staList.copy()
    colName.insert(0, 'Bus')
    colValue = ['' for i in range(len(colName))]
    # 列表不会吞重复值
    rowDic = dict(zip(colName, colValue))
    global tableInfo
    tableInfo = pd.DataFrame(data=None, columns=colName)

    global Bus_Dic
    Bus_Dic = {}

    CreateTime = time.strftime('%H%M')
    CsvName = 'New-' + '51-' + '0-' + CreateTime + '.csv'

    #MainPart
    while True:
        for _ in range(20):
            busdata_txt = getbusinfo(head, tail, bus_num, bus_dir)
            busdata = busdata_txt['data']['routeInfo']
            InfoList = generate_info(busdata)

            index_info = 0
            index_end = len(colName) - 1
            index_col = index_end
            time_str = time.strftime('%H%M%S')
            while (index_info < len(InfoList) and index_col > 0):

                if (InfoList[index_info]['staCode'] != colName[index_col]):
                    index_col -= 1
                    continue

                elif (InfoList[index_info]['status'] == 0):
                    index_info += 1
                    continue

                else:
                    RawBusPlate = InfoList[index_info]['busPlate']
                    NewBusPlate = CheckAndGenBusPlate(RawBusPlate)

                    ##到达终点站情形，避开特殊节点爬，默认已有前表
                    if (index_col == index_end):
                        if (NewBusPlate not in tableInfo['Bus'].values):
                            index_info += 1
                            continue
                        UpdateBusPlate(NewBusPlate)

                    CheckAddTable(NewBusPlate)
                    index_row = tableInfo[tableInfo.Bus == NewBusPlate].index.tolist()[0]
                    ##已有值则不添加
                    if (tableInfo.iloc[index_row, index_col] == ""):
                        tableInfo.iloc[index_row, index_col] = time_str
                    index_info += 1
            # tableInfo.to_csv(CsvName)
            time.sleep(8)


Main_Crawler()







