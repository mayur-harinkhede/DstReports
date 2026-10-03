from seatable_api import Base, context
server_url = context.server_url or 'https://cloud.seatable.io'
api_token = context.api_token or '37398967ccfa7a6acfc92e8224efa324b99310c3'
base = Base(api_token, server_url)
base.auth()

#Current time of a timezone
from datetime import datetime
import pytz
tz_Mumbai = pytz.timezone('Asia/Kolkata')
datetime_Mumbai = datetime.now(tz_Mumbai)
time=datetime_Mumbai.strftime('%H:%M')
today= datetime_Mumbai.strftime('%Y-%m-%d')

#ChatGpt function to convert array of dictionary ==>> array of array:
def dict_list_to_2d_array(dict_list):
    if not dict_list:
        return []

    headers = list(dict_list[0].keys())
    rows = [headers] + [[row[key] for key in headers] for row in dict_list]
    return rows

#Get Menu table for Menu and DOD:
rowsDate= base.query(f"select  *from Menu where Date > '{today}' Limit 1")
dateOfDelivery= rowsDate[0]["Date"]
rice= rowsDate[0]["Rice"]
dal= rowsDate[0]["Dal"]
curry= rowsDate[0]["Curry"]

menu=[rice,dal,curry,dateOfDelivery]

print(dateOfDelivery)


#Running SQL Query Below: 
#NOTE: Last Column is Route Name for Page Wise PDF filtering:   
rows= base.query(f"""select SchoolSr AS SrNo, School, 
EPS ,EUPS, EZPHS, ETotalAttendance AS ETotal,
PS, UPS, ZPHS, TotalAttendance as Total, 
`Rice 100%` AS R100 , `Rice 75%` AS R75 , `Rice 50%` AS R50 , `Rice 25%` AS R25 , `Rice 13%` AS R13, RiceVessels As Rice,
`Dal 150%` AS D150 , `Dal 100%` AS D100 , `Dal 75%` AS D75 , `Dal 50%` AS D50 , `Dal 25%` AS D25 , `Dal 13%` AS D13 , DalVessels As Dal,
`Curry 100%` AS C100,`Curry 75%` AS C75 , `Curry 50%` AS C50 , `Curry 25%` AS C25 , `Curry 13%` AS C13, CurryVessels As Curry,
CurdKg, SnacksFinal as SnackKg,
replace(EPS,0,5," ")AS Time, replace(EPS,0,5," ")AS `    Signature    `,
Route
from `Daily Indent` WHERE DOD = '{dateOfDelivery}' ORDER BY Route, SchoolSr LIMIT 10000""")


#Converting array of dictionary ==>> array of array:
result = dict_list_to_2d_array(rows)


#Creating new array of unique routes for each route delivery reports:
routeArray=[]
for row in rows:
    if row["Route"] not in routeArray:
        routeArray.append(row["Route"])

#Further Changes required: ,  menu  . Check sequence of rows.

#Sql 
TitleArray=['SrNo', 'School', 'PS', 'UPS', 'ZPHS', 'Total', 'PS', 'UPS', 'ZPHS', 'Total', '100%', '75%', '50%', '25%', '13%', 'Total', '150%', '100%', '75%', '50%', '25%', '13%', 'Total', '100%', '75%', '50%', '25%', '13%', 'Total', 'Curd', 'Snack', 'Time', 'Signature   ']

result[0]=TitleArray


