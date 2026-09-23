import uos
import time
from urtc import tuple2seconds, seconds2tuple


class BadgingStatus:
    OK = 0
    INVALID = 1
    NOT_THALES = 2
    PASSBACK = 3


class AttendanceModel:
    
    def __init__(self, rtc, datafilename='/sd/data.txt', statsfilename='/sd/stats.csv', passback=3600):
        self.datafilename = datafilename
        self.log = []
        self.last_visits = {}
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.passback = passback
        self.rtc = rtc
        self.monthly_line_counts = {}
        self.monthly_unique_ids = {}

        
    def read_data(self) -> Integer:
        try:
            print(uos.stat(self.datafilename))
        except:
            print("Error on stat")
            return -1
        
        result = {}
        with open(self.datafilename, 'r') as data_file:
            print("Reading data file")
            for line in data_file:
                try:
                    s_date, badge = line.split(',')
                    badge = badge.strip()
                    print(line.strip())
                    # convert here s_date into time
                    time_tuple = self.string_to_time_tuple(s_date.strip())
                    seconds = time.mktime(time_tuple)
                    # assumption : sorted chronologically
                    result[badge.strip()] = seconds
                    self.append_visit(badge, seconds)
                    #self.log.append([seconds, badge])
                    #self.last_visits[badge]=seconds
                except:
                    print(f"An error occured during treatment of line:\n {line}\n")
                
            print(f"Log initialized with {len(self.log)} entries")
            for key, value in self.last_visits.items():
                year, month, day, hour, minute, second, weekday, _yday = time.localtime(value)
                print(f"Last visit of {key} : {day}/{month}/{year} {hour}:{minute}:{second}")        
            self.export_stats()   
        return 0
    
    def append_visit(self, badge: str, timestamp: Integer):
        month = self.seconds_to_month(timestamp)
        self.log.append([timestamp, badge])
        self.last_visits[badge]=timestamp
        
        # stats
        if month not in self.monthly_line_counts:
            self.monthly_line_counts[month] = 0
            self.monthly_unique_ids[month] = set()
        self.monthly_line_counts[month] += 1
        self.monthly_unique_ids[month].add(badge)
        
    def export_stats(self):
        print(f"Total visits: {len(self.log)}")
        print(f"Unique visitors: {len(self.last_visits)}")
        for month in sorted(self.monthly_line_counts.keys()):
            print(f"{month}: visits={self.monthly_line_counts[month]}, unique:{len(self.monthly_unique_ids[month])}")
            
    def export_stats_to_csv(self, filename='/sd/stats.csv'):
        with open(filename, "w") as file:
            file.write(f"Stats Fablab\r\n")
            file.write(f"Nombre total de visites:, {len(self.log)}\r\n")
            file.write(f"Nombre de visiteurs uniques:, {len(self.last_visits)}\r\n")
            file.write(",")
            for month in sorted(self.monthly_line_counts.keys()):
                file.write(f"{month},")
            file.write("\r\ntotal,")
            for month in sorted(self.monthly_line_counts.keys()):
                file.write(f"{self.monthly_line_counts[month]},")
            file.write("\r\nuniques,")
            for month in sorted(self.monthly_line_counts.keys()):
                file.write(f"{len(self.monthly_unique_ids[month])},")
            file.write("\r\n")
    
    def string_to_time_tuple(self, time_str, fmt="%Y-%m-%d %H:%M:%S"):
    # Example parsing for YYYY-MM-DD HH:MM:SS
    # Note: MicroPython does not have strptime, so manual parsing is required
        try:
            parts = time_str.split()
            date_parts = parts[0].split('-')
            time_parts = parts[1].split(':')
            
            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2])
            
            # You may need to calculate weekday and yearday manually 
            # or use time.mktime() if your port supports it on partial tuples.
            # A common approach is to create a tuple and convert:
            temp_tuple = (year, month, day, hour, minute, second, 0, 0)
            
            # If mktime is available, it can help validate/convert
            # timestamp = time.mktime(temp_tuple)
            # return time.localtime(timestamp)
            
            return temp_tuple
        except (ValueError, IndexError):
            return None
        
    def visits(self) -> Integer:
        return len(self.log)
    
    def seconds_to_month(self, timestamp : Integer) -> str:
        time_tuple = seconds2tuple(timestamp)
        month = f"{time_tuple.year:04d}-{time_tuple.month:02d}"
        return month
    
    def write_visit(self, uid: str, timestamp: Integer):
        numbers = [i for i in uid]
        badge_ID = '{}-{}-{}-{}'.format(*numbers)

        time_tuple = seconds2tuple(timestamp)
        sdate = f"{time_tuple.year:04d}-{time_tuple.month:02d}-{time_tuple.day:02d}"
        stime = f"{time_tuple.hour:02d}:{time_tuple.minute:02d}:{time_tuple.second:02d}"
        
        with open(self.datafilename, "a") as file:
            print(f"writing: {sdate} {stime}, {badge_ID}\r\n")
            file.write(f"{sdate} {stime}, {badge_ID}\r\n")

        return
    
    def handle_event(self, uid: str, msg_length: Integer) -> BadgingStatus:
        if uid == None:
            return BadgingStatus.INVALID
        if (len(uid) != 4) or (msg_length != 30):
            return BadgingStatus.NOT_THALES
        # OK, thales signature
        numbers = [i for i in uid]
        badge_ID = '{}-{}-{}-{}'.format(*numbers)
        current_time_tuple = self.rtc.datetime()
        current_time = tuple2seconds(current_time_tuple)
        if badge_ID in self.last_visits.keys():
            last_visit = self.last_visits[badge_ID]           
            print(f"badge : {badge_ID} , last visit:{last_visit} time: {current_time} diff:{current_time - last_visit} passback:{self.passback}")
            if last_visit is not None:
                diff = current_time - last_visit
                if diff < self.passback:
                    return BadgingStatus.PASSBACK
        
        #self.last_visits[badge_ID] = current_time
        print(f"badge ok : {badge_ID} , time: {current_time}")
        self.append_visit(badge_ID, current_time)
        #self.log.append([current_time, badge_ID])
        self.write_visit(uid, current_time)
        
        return BadgingStatus.OK
        
        
       
       
if __name__ == "__main__":
    model =  AttendanceModel()
    model.read_data()