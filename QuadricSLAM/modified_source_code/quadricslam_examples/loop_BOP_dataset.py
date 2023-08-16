# create a loop to run through all the dataset
import subprocess
import psutil
import time


# Replace 'your_script.py' with the path to the Python file you want to run
script_path = 'BOP_YCB_dataset_test.py'
data_path = '/home/allen/Desktop/BOP_dataset_oaslam/ycbv/test/0000'

for i in range(48,60):
    # Run the Python script with arguments in a subprocess
    print(i)
    process_sub = subprocess.Popen(['python3', script_path, data_path+str(i)])

    while process_sub.poll() is None:
        time.sleep(5)