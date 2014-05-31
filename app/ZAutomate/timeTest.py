import time
import datetime
print time.asctime(time.localtime(time.time()))
ttime = time.localtime(time.time())
ctime = ""
for tt in ttime:
	ctime += (str)(tt)+":"
print ctime

relevantInsertTime = datetime.datetime.now().replace(minute=0,second=0, microsecond=0) 
###YATES_COMMENT: This adds the minutebreak (when we want to insert) to
###                    the relevantInsertTime.
###                    relevantInserTime = today:thisHouse:minuteBreak:00:00
relevantInsertTime += datetime.timedelta(minutes=30) #hours=1
print (str)(relevantInsertTime)
