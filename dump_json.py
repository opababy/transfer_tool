import json
import os
#import hashlib


class JsonData():
    def __init__(self, data_path, key, point_data):
        """
        test dtype
        [(404, 190), (652, 221), (619, 329), (406, 305)]
        """
        self.data_path = data_path
        self.key = key
        self.point_data = point_data
        
        # time stamp
        self.time_ori = None
        self.time_new = None
        
    def json_load(self):
        """
        argument newline
        https://stackoverflow.com/questions/61861172/what-does-the-argument-newline-do-in-the-open-function
        """
        # Record time stamp
        self.time_ori = os.path.getmtime(self.data_path)
        #print(self.time_ori)        
        
        with open(self.data_path, newline='') as jsonfile:
            self.data = json.load(jsonfile)
            #print(self.data)
            
    def json_data_process(self):
        #print(self.data)
        #print(self.data[self.key])
        """
        dtype
        {'p0': {'x': 0, 'y': 320}, 'p1': {'x': 201, 'y': 320}, 'p2': {'x': 391, 'y': 415}, 'p3': {'x': 0, 'y': 415}, 'p4': {'x': 0, 'y': 0}}
        """
        coordinate = {}
        
        for i in range(len(self.point_data)):
            coordinate["x"] = self.point_data[i][0]
            coordinate["y"] = self.point_data[i][1]
            #print(coordinate)
            """
            https://www.delftstack.com/zh-tw/howto/python/python-copy-dictionary/
            """
            self.data[self.key]["p%d"%i] = coordinate.copy() # Note! shallow copy
            
        #print("==================================================")
        #print(self.data[self.key])
        #print(self.data)
        
    def json_dump(self):
        with open(self.data_path, 'w', newline='') as jsonfile:
            json.dump(self.data, jsonfile, indent=4)
            
        # Record time stamp
        self.time_new = os.path.getmtime(self.data_path)
        #print(self.time_new)
        
    def check_json_file_exist(self):
        if os.path.isfile(self.data_path):
            return True
        
        return False
        
    def check_json_file_update(self):
        # Check time stamp changed
        # # Check SHA changed
        # """ 
        # https://blog.gtwang.org/programming/python-md5-sha-hash-functions-tutorial-examples/
        # """
        if self.time_ori != self.time_new:
            return True
        
        return False
            
def main():           
    jsonData = JsonData("data/event_fusion.json", "bsd_roi1", [(404, 190), (652, 221), (619, 329), (406, 305)])
    jsonData.json_load()
    jsonData.json_data_process()
    jsonData.json_dump()
    print(jsonData.check_json_file_update())
    
    
if __name__ == "__main__":
    main()