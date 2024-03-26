'''
Convert a downloaded json file to a csv file
In the generated csv file: 1st column is the date&time
the rest columns are data from sensors.
The first row is the index, indicating the meaning
of each column values. 

#Usage example: if the data is published from a Raspberry pi
#JSON_FILE = 'rtdb-sensor1-export.json'
#CSV_FILE = 'sensor1.csv'
#convert_json2csv(JSON_FILE, CSV_FILE, isNodeMCU=False) 

Modified March 2024
by Jin Zhu

# required package: pandas 
# to install: pip install pandas

'''

from datetime import datetime
import pandas as pd
import csv

def convert_json2csv(json_filename, csv_filename, isNodeMCU): 
    with open(json_filename, encoding='utf-8') as inputfile:
        df = pd.read_json(inputfile)

    n_rows = df.shape[0]  #obtain the number of fields for each entry(object)
    n_cols = df.shape[1]  #obtain the number of entries
    #print(n_rows, ' x ')
    #print(n_cols)

    with open(csv_filename, 'w', newline='') as csvfile:
        writer =csv.writer(csvfile)
        #print(df.index)
        if (isNodeMCU==True):
            writer.writerow(df.index)  #write the column index (fields) into the file
        else:       #remove the first two fields 'Date' and 'Time' and replace with 'Timestamp'
            fields = ['Timestamp'] + df.index[2:].tolist()
            print(fields)
            writer.writerow(fields)
        
        for idx in df.columns:
            data=[]
            if (isNodeMCU==True):  #Change timestamp to datetime
                data.append(str(datetime.fromtimestamp(df[idx][0]/1000)))
                for j in range(1,n_rows): #obtain each entry and convert it to a list
                    data.append(df[idx][j])
            else: #combine date and time into one field if it is from Raspberry pi
                combinedt = str(df[idx][0])+' ' + str(df[idx][1])
                data.append(combinedt)
                for j in range(2,n_rows): #obtain each entry and convert it to a list
                    data.append(df[idx][j])
            #print(data)
            writer.writerow(data)    #write the row into the csv file        


