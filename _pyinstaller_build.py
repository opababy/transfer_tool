# -*- coding: utf-8 -*-
import os, sys
import shutil


OUTPUT_FOLDER = "dist"
SRC_FILES = ["run.py"]

def main():
    try:
        shutil.rmtree(OUTPUT_FOLDER)
    except OSError as e:
        print('INFO: erase folder %s failed (%s)\n' % (OUTPUT_FOLDER, e.strerror))

    for src_file in SRC_FILES:
        os.system('pyinstaller -F %s' % src_file)
        dst_file = os.path.join(OUTPUT_FOLDER, src_file.split('.')[0]+'.exe')
        if os.path.isfile(dst_file):
            print ('%s build done\n' % dst_file)
        else: 
            print ('%s build failed\n' % dst_file)
            return
    
    shutil.copytree('config', os.path.join(OUTPUT_FOLDER, 'config'))
    shutil.copytree('icon', os.path.join(OUTPUT_FOLDER, 'icon'))
    shutil.copytree('data', os.path.join(OUTPUT_FOLDER, 'data'))
    shutil.copytree('images', os.path.join(OUTPUT_FOLDER, 'images'))
    shutil.copytree('videos', os.path.join(OUTPUT_FOLDER, 'videos'))
        
    # for numpyDLL in ['libiomp5md.dll', 'mkl_core.dll', 'mkl_def.dll', 'mkl_intel_thread.dll', 'libifcoremd.dll', 'libmmd.dll']:
        # try:
            # shutil.copyfile(os.path.join(os.path.dirname(os.__file__), 'site-packages', 'numpy', 'DLLs', numpyDLL), os.path.join(OUTPUT_FOLDER, numpyDLL))
        # except OSError as e:
            # print('ERROR: copy %s failed (%s)\n' % (numpyDLL, e.strerror))
            # return
    
    
if __name__== "__main__":
    main()

