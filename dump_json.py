import json
import os


class JsonData():
    def __init__(self, key, point_data):
        """
        test dtype
        [(404, 190), (652, 221), (619, 329), (406, 305)]
        """
        self.data_path = "data/event_fusion.json"
        self.new_data_path = self.data_path.strip().split('.')[0] + "_new.json"
        
        self.key = key
        self.point_data = point_data
        
    def json_load(self):
        """
        argument newline
        https://stackoverflow.com/questions/61861172/what-does-the-argument-newline-do-in-the-open-function
        """
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
        with open(self.new_data_path, 'w', newline='') as jsonfile:
            json.dump(self.data, jsonfile, indent=4)
            
    def check_new_json_file(self):
        if os.path.isfile(self.new_data_path):
            return True
        
        return False
            
def main():           
    jsonData = JsonData("bsd_roi1", [(404, 190), (652, 221), (619, 329), (406, 305)])
    jsonData.json_load()
    jsonData.json_data_process()
    jsonData.json_dump()
    
    
if __name__ == "__main__":
    main()