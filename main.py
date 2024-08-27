import threading
import requests
import AngelIntegration,AliceBlueIntegration
import time
import traceback
from datetime import datetime, timedelta
import pandas as pd
result_dict={}
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta

AliceBlueIntegration.load_alice()
AliceBlueIntegration.get_nfo_instruments()

# project

def convert_julian_date(date_object):
    year = date_object.year
    month = date_object.month
    day = date_object.day
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn


def get_delta(strikeltp,underlyingprice,strike,timeexpiery,riskfreeinterest,flag):
    # flag me  call  'c' ya put 'p'
    from py_vollib.black_scholes.greeks.analytical import delta
    iv= implied_volatility(price=strikeltp,S=underlyingprice,K=strike,t=timeexpiery,r=riskfreeinterest,flag=flag)
    value = delta(flag,underlyingprice,strike,timeexpiery,riskfreeinterest,iv)
    print("delta",value)
    return value


def option_delta_calculation(symbol,expiery,Tradeexp,strike,optiontype,underlyingprice,MODE):
    date_obj = datetime.strptime(Tradeexp, "%d-%b-%y")
    formatted_date = date_obj.strftime("%d%b%y").upper()
    optionsymbol = f"{symbol}{formatted_date}{strike}{optiontype}"
    optionltp=AngelIntegration.get_ltp(segment="NFO", symbol=optionsymbol,
                             token=get_token(optionsymbol))
    if MODE == "WEEKLY":
        date_object = datetime.strptime(expiery, '%d-%b-%y')
        distanceexp = convert_julian_date(date_object)
        print("WEEKLY: ",distanceexp)
    if MODE == "MONTHLY":
        distanceexp = datetime.strptime(expiery, "%d-%b-%y")  # Convert string to datetime object if necessary
        print("MONTHLY: ",distanceexp)
    t= (distanceexp-datetime.now())/timedelta(days=1)/365
    print("t: ",t)
    if optiontype=="CE":
        fg="c"
    else :
        fg = "p"
    value=get_delta(strikeltp=optionltp, underlyingprice=underlyingprice, strike=strike, timeexpiery=t,flag=fg ,riskfreeinterest=0.1)
    return value

def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder
    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)
    rounded_dt = rounded_dt.replace(second=0, microsecond=0)
    return rounded_dt

def determine_min(minstr):
    min = 0
    if minstr == "1":
        min = 1
    if minstr == "3":
        min = 3
    if minstr == "5":
        min = 5
    if minstr == "15":
        min = 15
    if minstr == "30":
        min = 30

    return min

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
def get_user_settings():
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Tp1Qty,Tp2Qty,
            # Symbol,Quantity,EXPIERY,TimeFrame,TF_INT,BASESYMBOL,USE_CPR,PartialProfitQty,Atr_Period,Atr_Multiplier,
            # EntryTime,ExitTime,strikestep,StrikeNumber,USEEXPIERY,TradeExpiery,AliceblueTradeExp,PRODUCT_TYPE
            symbol_dict = {
                'Symbol': row['Symbol'],"Quantity":row['Quantity'],
                'EXPIERY': row['EXPIERY'], "EntryVariable": row['EntryVariable'],
                 "BASESYMBOL": row['BASESYMBOL'],'USE_CPR': row['USE_CPR'],
                'exch':None,
                'EntryTime': row['EntryTime'], "ExitTime": row['ExitTime'],
                'strikestep': row['strikestep'], "StrikeNumber": row['StrikeNumber'],
                'USEEXPIERY': row['USEEXPIERY'], "TradeExpiery": row['TradeExpiery'],'SLvariable': row['SLvariable'],
                'AliceblueTradeExp': row['AliceblueTradeExp'], "PRODUCT_TYPE": row['PRODUCT_TYPE'],"InitialOnce":None,
                'FifteenHigh': None, "FifteenLow":None,"Bp":None,"Sp":None,"SL_level":0,"T1_level":0,"T2_level":0,'Trade':None,
                'Tsl':None,"pphit":None,'Tp1Qty':row['Tp1Qty'],'Tp2Qty':row['Tp2Qty'],"BUY":False,"SHORT":False,"ReversalLevel":0,"T2Done":False,
                'Previoustrade':None,"RevTrade":False,"aliceexp": None,"producttype":row['PRODUCT_TYPE'],
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

get_user_settings()
def get_api_credentials():
    credentials = {}

    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


credentials_dict = get_api_credentials()
stockdevaccount=credentials_dict.get('stockdevaccount')
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)

AngelIntegration.symbolmpping()


def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token

def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def getstrikes_put(ltp, step , strikestep):
    result = {}
    result[int(ltp)] = None

    for i in range(step):
        result[int(ltp + strikestep * (i + 1))] = None
    return result

def getstrikes_call(ltp, step , strikestep):
    result = {}
    result[int(ltp)] = None
    for i in range(step):
        result[int(ltp - strikestep * (i + 1))] = None

    return result


def get_max_delta_strike(strikelist):
    max_delta = -float("inf")  # Initialize with negative infinity
    max_delta_strike = None
    for strike, delta in strikelist.items():
        if delta > max_delta:
            max_delta = delta
            max_delta_strike = strike
    return max_delta_strike

def round_to_nearest(number, nearest):
    return round(number / nearest) * nearest


def main_strategy():
    print("main_strategy running ")
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")

            if isinstance(symbol_value, str):
                if params["InitialOnce"]==None:
                    params["InitialOnce"] ="DONE"
                    initialdata= AngelIntegration.get_historical_data(symbol=params['Symbol'],token=get_token(params['Symbol']),\
                                                                      timeframe="FIFTEEN_MINUTE",segment='NSE')
                    params['FifteenHigh']= initialdata.iloc[-2]['high']
                    params['FifteenLow']= initialdata.iloc[-2]['low']
                    params["Bp"]=  ((params['FifteenHigh']+params['FifteenLow'])/2)+ params['EntryVariable']
                    params["Sp"]=  ((params['FifteenHigh']+params['FifteenLow'])/2)- params['EntryVariable']


                ltp=AngelIntegration.get_ltp(segment='NSE',symbol=params['Symbol'],token=get_token(params['Symbol']))

                print(f"FifteenHigh:{params['FifteenHigh']}, FifteenLow:{params['FifteenLow']}, BuyPrice: {params['Bp']},SellPrice: {params['Sp']},"
                      f"SL_level: {params['SL_level']} ,T1_level: {params['T1_level']} ,T2_level: {params['T2_level']} ,"
                      f"ReversalLevel:{params['ReversalLevel']}, Trade : {params['Trade']}, T2Done :{params['T2Done']}")


                if ltp >=  params['ReversalLevel'] and params["T2Done"] == True and params['Trade']=="BUY" and  params['ReversalLevel']>0:
                    params['ReversalLevel']=0
                    params["RevTrade"]= True
                    params['Trade'] = "SHORT"
                    OrderLog = f"{timestamp} Reverse Sell initiated @ {params['Symbol']} @ {ltp} "
                    write_to_order_logs(OrderLog)
                    params["SL_level"] = (((params['FifteenHigh']+params['FifteenLow'])/2)+(params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) + ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))+ params['SLvariable']

                    params["T1_level"] =((params['FifteenHigh']+params['FifteenLow'])/2)+  ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))  + (params['FifteenHigh']-params['FifteenLow'])

                    params["T2_level"] =((params['FifteenHigh']+params['FifteenLow'])/2)+ (params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))

                    params["pphit"] = "NOHIT"
                    strikelist = getstrikes_put(
                        ltp=round_to_nearest(number=ltp, nearest=params['strikestep']),
                        step=params['StrikeNumber'],
                        strikestep=params['strikestep'])
                    print("Strikes to check for delta put:", strikelist)
                    for strike in strikelist:
                        date_format = '%d-%b-%y'

                        delta = float(
                            option_delta_calculation(symbol=params['BASESYMBOL'], expiery=str(params['TradeExpiery']),
                                                     Tradeexp=params['TradeExpiery'],
                                                     strike=strike,
                                                     optiontype="PE",
                                                     underlyingprice=ltp,
                                                     MODE=params["USEEXPIERY"]))
                        strikelist[strike] = delta

                    print("strikelist: ", strikelist)
                    final = get_max_delta_strike(strikelist)
                    print("Final strike: ", final)
                    params['putstrike'] = final
                    optionsymbol = f"NSE:{symbol}{params['TradeExpiery']}{final}PE"
                    params['exch'] = "NFO"

                    aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                    aliceexp = aliceexp.strftime('%Y-%m-%d')
                    params['aliceexp'] = aliceexp
                    print("exch: ", params['exch'])
                    print("symbol: ", symbol)

                    AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                             symbol=params['BASESYMBOL'],
                                             expiry_date=params['aliceexp'],
                                             strike=params['putstrike'], call=False, producttype=params["producttype"])

                    OrderLog = f"{timestamp} Reverse Sell @ {params['Symbol']} @ {ltp} option contract : {optionsymbol}, initial sl ={params['SL_level']}, T1={params['T1_level']},T2={params['T2_level']}"
                    write_to_order_logs(OrderLog)

                if ltp <=params['ReversalLevel'] and params["T2Done"] == True and params['Trade']=="SHORT" and  params['ReversalLevel']>0:
                    params['ReversalLevel']= 0
                    OrderLog = f"{timestamp} Reverse Buy initiated @ {params['Symbol']} "
                    print(OrderLog)
                    params["RevTrade"] = True
                    params['Trade'] = "BUY"
                    write_to_order_logs(OrderLog)
                    params["SL_level"] =((params['FifteenHigh']+params['FifteenLow'])/2)- ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) -  ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) - params['SLvariable']

                    params["T1_level"] = ((params['FifteenHigh']+params['FifteenLow'])/2)- ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))-(params['FifteenHigh']-params['FifteenLow'])

                    params["T2_level"] =((params['FifteenHigh']+params['FifteenLow'])/2) - ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))

                    params["pphit"] = "NOHIT"
                    strikelist = getstrikes_call(
                        ltp=round_to_nearest(number=ltp, nearest=params['strikestep']),
                        step=params['StrikeNumber'],
                        strikestep=params['strikestep'])
                    print("Strikes to check for delta call:", strikelist)
                    for strike in strikelist:
                        date_format = '%d-%b-%y'

                        delta = float(
                            option_delta_calculation(symbol=params['BASESYMBOL'], expiery=str(params['TradeExpiery']),
                                                     Tradeexp=params['TradeExpiery'],
                                                     strike=strike,
                                                     optiontype="CE",
                                                     underlyingprice=ltp,
                                                     MODE=params["USEEXPIERY"]))
                        strikelist[strike] = delta

                    print("strikelist: ", strikelist)
                    final = get_max_delta_strike(strikelist)
                    print("Final strike: ", final)
                    params['callstrike'] = final

                    optionsymbol = f"NSE:{symbol}{params['TradeExpiery']}{final}CE"
                    params['exch'] = "NFO"

                    aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                    aliceexp = aliceexp.strftime('%Y-%m-%d')
                    params['aliceexp'] = aliceexp
                    print("exch: ", params['exch'])

                    AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                             symbol=params['BASESYMBOL'],
                                             expiry_date=params['aliceexp'],
                                             strike=params['callstrike'], call=True, producttype=params["producttype"])
                    OrderLog = f"{timestamp} Reverse Buy @ {params['Symbol']} option contract : {optionsymbol}, initial sl ={params['SL_level']}, T1={params['T1_level']},T2={params['T2_level']}"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)





                if ltp>=params["Bp"] and params["Bp"] is not None and params['Trade']==None and params["BUY"]== False:
                    params['Trade']="BUY"
                    params["BUY"]= True
                    params["SHORT"]= False
                    OrderLog=f"{timestamp} Buy @ {params['Symbol']} @ {ltp}"
                    params["pphit"] = "NOHIT"
                    params["SL_level"] = ((params['FifteenHigh']+ params['FifteenLow'])/2)-params['SLvariable']
                    params["T1_level"] = ((params['FifteenHigh']+params['FifteenLow'])/2)+  ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))
                    params["T2_level"] = (((params['FifteenHigh']+params['FifteenLow'])/2) + ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))) + (params['FifteenHigh']-params['FifteenLow'])
                    print("T1_level: ", params["T1_level"])
                    print("T2_level: ", params["T2_level"])
                    write_to_order_logs(OrderLog)
                    strikelist = getstrikes_call(
                        ltp=round_to_nearest(number=ltp, nearest=params['strikestep']),
                        step=params['StrikeNumber'],
                        strikestep=params['strikestep'])
                    print("Strikes to check for delta call:", strikelist)
                    for strike in strikelist:
                        date_format = '%d-%b-%y'

                        delta = float(
                            option_delta_calculation(symbol=params['BASESYMBOL'], expiery=str(params['TradeExpiery']),
                                                     Tradeexp=params['TradeExpiery'],
                                                     strike=strike,
                                                     optiontype="CE",
                                                     underlyingprice=ltp,
                                                     MODE=params["USEEXPIERY"]))
                        strikelist[strike] = delta

                    print("strikelist: ", strikelist)
                    final = get_max_delta_strike(strikelist)
                    print("Final strike: ", final)
                    params['callstrike'] = final

                    optionsymbol = f"NSE:{params['BASESYMBOL']}{params['TradeExpiery']}{final}CE"
                    params['exch'] = "NFO"

                    aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                    aliceexp = aliceexp.strftime('%Y-%m-%d')
                    params['aliceexp'] = aliceexp
                    print("exch: ", params['exch'])

                    AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                             symbol=params['BASESYMBOL'],
                                             expiry_date=params['aliceexp'],
                                             strike=params['callstrike'], call=True, producttype=params["producttype"])
                    OrderLog = f"{timestamp} Buy @ {params['Symbol']} option contract : {optionsymbol}, initial sl ={params['SL_level'] }, T1={params['T1_level'] },T2={params['T2_level'] }"
                    print(OrderLog)
                    write_to_order_logs(OrderLog)

                if ltp<=params["Sp"] and params["Sp"] is not None and params['Trade']==None and params["SHORT"] == False:
                    params['Trade'] = "SHORT"
                    params["pphit"] = "NOHIT"
                    params["BUY"] = False
                    params["SHORT"] = True
                    OrderLog=f"{timestamp} Sell @ {params['Symbol']} @ {ltp}"
                    write_to_order_logs(OrderLog)

                    params["SL_level"] = ((params['FifteenHigh']+ params['FifteenLow'])/2)+params['SLvariable']
                    params["T1_level"] = ((params['FifteenHigh']+params['FifteenLow'])/2)- ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))
                    params["T2_level"] = ((params['FifteenHigh']+params['FifteenLow'])/2) - ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))- (params['FifteenHigh']-params['FifteenLow'])
                    print("T1_level: ",params["T1_level"])
                    print("T2_level: ",params["T2_level"] )
                    strikelist = getstrikes_put(
                        ltp=round_to_nearest(number=ltp, nearest=params['strikestep']),
                        step=params['StrikeNumber'],
                        strikestep=params['strikestep'])
                    print("Strikes to check for delta put:", strikelist)
                    for strike in strikelist:
                        date_format = '%d-%b-%y'

                        delta = float(
                            option_delta_calculation(symbol=params['BASESYMBOL'], expiery=str(params['TradeExpiery']),
                                                     Tradeexp=params['TradeExpiery'],
                                                     strike=strike,
                                                     optiontype="PE",
                                                     underlyingprice=ltp,
                                                     MODE=params["USEEXPIERY"]))
                        strikelist[strike] = delta

                    print("strikelist: ", strikelist)
                    final = get_max_delta_strike(strikelist)
                    print("Final strike: ", final)
                    params['putstrike'] = final
                    optionsymbol = f"NSE:{symbol}{params['TradeExpiery']}{final}PE"
                    params['exch'] = "NFO"

                    aliceexp = datetime.strptime(params['AliceblueTradeExp'], '%d-%b-%y')
                    aliceexp = aliceexp.strftime('%Y-%m-%d')
                    params['aliceexp'] = aliceexp
                    print("exch: ", params['exch'])
                    print("symbol: ", symbol)

                    AliceBlueIntegration.buy(quantity=int(params["Quantity"]), exch=params['exch'],
                                             symbol=params['BASESYMBOL'],
                                             expiry_date=params['aliceexp'],
                                             strike=params['putstrike'], call=False, producttype=params["producttype"])

                    OrderLog = f"{timestamp} Sell @ {params['Symbol']} @ {ltp} option contract : {optionsymbol}, initial sl ={params['SL_level'] }, T1={params['T1_level'] },T2={params['T2_level'] }"
                    write_to_order_logs(OrderLog)

                if params['Trade']=="BUY":
                    if ltp >=  params['T1_level'] and params['T1_level']>0:
                        params['Tsl']= (((params['FifteenHigh']+params['FifteenLow'])/2)+(params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) -  (params['FifteenHigh']-params['FifteenLow'])

                        if params["RevTrade"]==True:
                            params['Tsl'] =(((params['FifteenHigh']+params['FifteenLow'])/2)+(params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) + ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))

                        params['SL_level']=params['Tsl']
                        params["pphit"] ="HIT"
                        params['T1_level'] = 0
                        params["Remainingqty"] = params["Quantity"]-params["Tp1Qty"]
                        OrderLog = f"{timestamp} Buy T1 executed  @ {ltp} option contract : {params['Symbol']} new sl level = {params['Tsl']}"
                        write_to_order_logs(OrderLog)
                        AliceBlueIntegration.buyexit(quantity=params["Tp1Qty"], exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params["callstrike"], call=True,
                                                     producttype=params["producttype"])

                    if ltp >=  params['T2_level'] and params['T2_level']>0:
                        OrderLog = f"{timestamp} Buy T2 executed  @ {ltp} option contract : {params['Symbol']}"
                        write_to_order_logs(OrderLog)
                        params["pphit"] = "HIT"
                        params["Remainingqty"] = 0
                        params['T2_level']=0
                        params["T2Done"] = True
                        params['ReversalLevel']=(((params['FifteenHigh']+ params['FifteenLow'])/2)+(params['FifteenHigh']- params['FifteenLow'])+(0.618*(params['FifteenHigh']- params['FifteenLow']))) + ((params['FifteenHigh']- params['FifteenLow'])+(0.618*(params['FifteenHigh']- params['FifteenLow'])))
                        params['T2_level'] =0

                        AliceBlueIntegration.buyexit(quantity=params["Tp2Qty"], exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params["callstrike"], call=True,
                                                     producttype=params["producttype"])


                    if params["SL_level"] >0 and ltp<=params["SL_level"]:
                        if params["pphit"] == "NOHIT":
                            OrderLog = f"{timestamp} Stoploss  booked buy trade @ {symbol} @ {ltp}, lotsize={params['Quantity']}"
                            print(OrderLog)
                            params['SL_level'] = 0
                            write_to_order_logs(OrderLog)
                            params["pphit"] = "NOMORETRADES"
                            params['Trade']=None

                            AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch=params['exch'],
                                                         symbol=params['BASESYMBOL'],
                                                         expiry_date=params['aliceexp'],
                                                         strike=params["callstrike"], call=True,
                                                         producttype=params["producttype"])
                        if params["pphit"] == "HIT":
                            if params["Remainingqty"] >0:
                                params['Trade'] = None
                                params['SL_level'] = 0
                                OrderLog = f"{timestamp} Stoploss  booked buy trade @ {symbol} @ {ltp}, lotsize={params['Remainingqty']}"
                                print(OrderLog)
                                write_to_order_logs(OrderLog)
                                params["pphit"] = "NOMORETRADES"
                                AliceBlueIntegration.buyexit(quantity=params["Remainingqty"], exch=params['exch'],
                                                             symbol=params['BASESYMBOL'],
                                                             expiry_date=params['aliceexp'],
                                                             strike=params["callstrike"], call=True,
                                                             producttype=params["producttype"])

                            if params["Remainingqty"] == 0:
                                params['Trade'] = None
                                params['SL_level'] = 0
                                # OrderLog = f"{timestamp} Stoploss  booked buy trade @ {symbol} @ {params['previousBar_close']}, lotsize={params['Remainingqty']}"
                                # print(OrderLog)
                                # write_to_order_logs(OrderLog)
                                params["pphit"] = "NOMORETRADES"


                if params['Trade']=="SHORT":
                    if ltp <= params['T1_level'] and params['T1_level'] >0:
                        params['Tsl'] = ((params['FifteenHigh']+params['FifteenLow'])/2)-((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))+   (params['FifteenHigh']-params['FifteenLow'])

                        if params["RevTrade"]==True:
                            params['Tsl'] = ((params['FifteenHigh']+params['FifteenLow'])/2)- ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) -  ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))


                        params['SL_level']=params['Tsl']
                        params['T1_level'] = 0
                        OrderLog = f"{timestamp} Sell T1 executed  @ {ltp} option contract : {params['Symbol']} new sl level = {params['Tsl']}"
                        write_to_order_logs(OrderLog)
                        params["pphit"] = "HIT"
                        params["Remainingqty"] = params["Quantity"] - params["Tp1Qty"]
                        AliceBlueIntegration.buyexit(quantity=params["Tp1Qty"], exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params["putstrike"], call=False,
                                                     producttype=params["producttype"])

                    if ltp <= params['T2_level'] and params['T2_level'] >0:
                        OrderLog = f"{timestamp} Sell T2 executed  @ {ltp} option contract : {params['Symbol']}"
                        write_to_order_logs(OrderLog)
                        params["pphit"] = "HIT"

                        params["T2Done"] = True
                        params['T2_level']=0
                        params['ReversalLevel'] = ((params['FifteenHigh']+params['FifteenLow'])/2)- ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow']))) -  ((params['FifteenHigh']-params['FifteenLow'])+(0.618*(params['FifteenHigh']-params['FifteenLow'])))


                        AliceBlueIntegration.buyexit(quantity=params["Tp2Qty"], exch=params['exch'],
                                                     symbol=params['BASESYMBOL'],
                                                     expiry_date=params['aliceexp'],
                                                     strike=params["putstrike"], call=False,
                                                     producttype=params["producttype"])


                    if params["SL_level"] >0 and ltp >= params["SL_level"]:
                        if params["pphit"] == "NOHIT":
                            params['Trade'] = None
                            params['SL_level'] = 0
                            OrderLog = f"{timestamp} Stoploss  booked sell trade @ {symbol} @ {ltp}, lotsize={params['Quantity']}"
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            params["pphit"]="NOMORETRADES"
                            AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch=params['exch'],
                                                         symbol=params['BASESYMBOL'],
                                                         expiry_date=params['aliceexp'],
                                                         strike=params["putstrike"], call=False,
                                                         producttype=params["producttype"])

                        if params["pphit"] == "HIT":
                            params['Trade'] = None
                            params['SL_level'] = 0
                            OrderLog = f"{timestamp} Stoploss  booked sell trade @ {symbol} @ {ltp}, lotsize={params['Remainingqty']}"
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            params["pphit"] = "NOMORETRADES"
                            AliceBlueIntegration.buyexit(quantity=params["Remainingqty"], exch=params['exch'],
                                                         symbol=params['BASESYMBOL'],
                                                         expiry_date=params['aliceexp'],
                                                         strike=params["putstrike"], call=False,
                                                         producttype=params["producttype"])




    except Exception as e:
        print("Error in main strategy : ", str(e))
        traceback.print_exc()


while True:
    main_strategy()
    time.sleep(2)
