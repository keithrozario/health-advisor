from datetime import datetime 
import pytz 
  
# get the standard UTC time  
UTC = pytz.utc 
  
# it will get the time zone  
# of the specified location 
SGT = pytz.timezone('Asia/Singapore') 
  
# print the date and time in 
# standard format 
print("UTC in Default Format : ",  
      datetime.now(UTC)) 
  
now = datetime.now(SGT).replace(second=0, microsecond=0).isoformat()
print(now)