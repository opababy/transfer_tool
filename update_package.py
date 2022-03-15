# -*- coding: utf-8 -*-
import os, sys
import shutil
import tarfile
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
""" https://learningsky.io/python-requests-insecurerequestwarning/ """

def update_package(ip="10.0.0.2"):
    # path 
    package_path = "alarm_calibration"
    tar_filename = "alarm_calibration.tar"
    json_path = "data"
    json_filename = "event_fusion.json"
    
    # copy json file to package
    shutil.copyfile(os.path.join(json_path, json_filename), os.path.join(package_path, json_filename))

    # generate install package
    if os.path.isfile(tar_filename):
        os.remove(tar_filename)

    # change the work directory => remember change back
    os.chdir("alarm_calibration")
    
    #print("generate "+tar_filename)
    tar_filename1 = os.path.join("..", tar_filename)
    tar = tarfile.open(tar_filename1, "w")
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            tar.add(file_name)
    tar.close()

    # upload package
    #print("upload package "+tar_filename)
    data = open(tar_filename1).read()
    
    try:
        r = requests.post("https://"+ip+"/packages",
                            auth=("test", "test"), verify=False, data=data)
                            
        #print(r)
        #print(r.text)
        
        if r.text.split(',')[0].split(':')[1].strip() == '\"success\"':
            return True
        return False
        
    except Exception as e:
        return False


def main():
    r = update_package(ip="10.0.0.2")
    print(r)


if __name__ == "__main__":
    main()
