# Retrive data from firebase realtime database using firebase-admin
#
# 
# Modified March 2024
# By Jin Zhu
# 
# required package: firebase-admin 
# pip install firebase-admin

import time
from datetime import datetime
import re
import sys
import json

#package used for firebase access
import firebase_admin
from firebase_admin import db

#retrieve data from rtdb_path for the duration between start and end_datetime
#save the data into json_file
def firebase_retrieve4datetime(rtdb_path, start_datetime, end_datetime, json_file):
     #ordering by a specified child key and using start_at() and end_at() to limit the query
     ref=db.reference(rtdb_path)
     start_time = datetime.timestamp(datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S'))
     end_time = datetime.timestamp(datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S'))
     #print(start_time, '  ', end_time)
     snapshot = ref.order_by_child('Timestamp').start_at(start_time*1000).end_at(end_time*1000).get()
     with open(json_file,'w') as file:
          json.dump(snapshot, file)
     
