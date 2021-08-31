import pandas as pd
import numpy as np
import sys
from datetime import datetime
from datetime import date
import time


#access data
try:
    df = pd.read_csv('rt_trips_DB_2018.txt', delimiter = ";")
    print("Data Access: Successful!\n")

except Exception as e:
    print("Data Access: Failed")
    print("Error message: ",e)
    print("Please try again\n")
    sys.exit()
    
    
#drop redundant data
redudantRows = ["DATASOURCE","BASIN","TENDERLOT","SUPPRESSED","JUSTIFICATIONID","LASTUPDATE","NOTE","Unnamed: 0"]
df.drop(columns=redudantRows, inplace=True)

#remove rows with missing values in key rows
df.dropna(subset=["ACTUALTIME_ARR"])
df.dropna(subset=["ACTUALTIME_DEP"])

#test target features
df["PLANNEDTIME_TOTAL"] = df["PLANNEDTIME_ARR"] - df["PLANNEDTIME_DEP"]
df["ACTUALTIME_TOTAL"] = df["ACTUALTIME_ARR"] - df["ACTUALTIME_DEP"]
df["DELAY"] = df["ACTUALTIME_TOTAL"] - df["PLANNEDTIME_TOTAL"]

#format date column to allow the data to be combined with open weather maps data
df['DATE'] = np.nan
for i in range(df.shape[0]):
    df['DATE'].iloc[i] = datetime.strptime(df['DAYOFSERVICE'].iloc[i], '%d-%b-%y 00:00:00')
    
#get hour and minutes
df["hours"] = df["ACTUALTIME_DEP"]//3600
df["minutes"] = ((df["ACTUALTIME_DEP"]/3600 - df["ACTUALTIME_DEP"]//3600)*60)//1

#create columns to record the month and day
df["month"] = np.nan
df["day"] = np.nan

for i in range(df.shape[0]):
        df["DATE"].iloc[i]= df["DATE"].iloc[i].replace(hour=int(df["hours"].iloc[i]), minute=int(df["minutes"].iloc[i]))
        df["month"].iloc[i] = df.DATE.iloc[i].month

df["month"] = df["month"].astype("int64")       

#get data ready to be stored in text file
df_final = df[["TRIPID","DATE","DIRECTION","PLANNEDTIME_TOTAL","ACTUALTIME_TOTAL","DELAY","LINEID","ROUTEID","hours","month","day"]]
df_final.DATE = df_final.DATE.astype('datetime64[ns]')
df_final.dtypes

#create column to reflect if day is a day of the week
df_final["weekend"] = np.logical_or(df_final["day"]== 5, df_final["day"]== 6)
df_final["weekend"].replace({False:0,True:1},inplace=True)
df_final["weekday"] = np.logical_or(df_final["day"]>5, df_final["weekend"]== 0)
df_final["weekday"].replace({False:0,True:1},inplace=True)

#add couln to record if bus traveling during rush hour
df_final["rush_hour"] = np.logical_or(df_final["hours"]== 7.0, df_final["day"]== 8.0)
df_final["rush_hour"] = np.logical_or(df_final["rush_hour"] == True, df_final["day"]== 16.0)
df_final["rush_hour"] = np.logical_or(df_final["rush_hour"] == True, df_final["day"]== 17.0)
df_final["rush_hour"].replace({False:0,True:1},inplace=True)

#save to csv
df_final.to_csv()