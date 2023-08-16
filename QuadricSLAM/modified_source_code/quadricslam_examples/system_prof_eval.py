import subprocess
import psutil
import time

# Replace 'your_script.py' with the path to the Python file you want to run
script_path = 'BOP_YCB_dataset_test.py'
data_path = '/home/allen/Desktop/BOP_dataset_quadricslam/ycbv/test/000048'


# Run the Python script with arguments in a subprocess
process_sub = subprocess.Popen(['python3', script_path, data_path])

# Get the PID of the process
process_pid = process_sub.pid

print(f"Process PID: {process_pid}")

process = psutil.Process(process_pid)


# Initialize variables for monitoring
cpu_percent_list = []
ram_usage_list = []
start_time = time.time()

#num_cores = psutil.cpu_count(logical=False)

# Monitor until the process dies
while process_sub.poll() is None:
    # Monitor CPU utilization
    cpu_percent_list.append(process.cpu_percent(interval=1)/8)
    # Monitor RAM utilization
    ram_usage_list.append(process.memory_info().rss)
    

end_time = time.time()
execution_time = end_time - start_time

cpu_percent_list = cpu_percent_list[2:-2]
ram_usage_list = ram_usage_list[2:-2]
divisor = 1024 * 1024
ram_usage_list = [element / divisor for element in ram_usage_list] # Convert from bytes to MB


indices_to_remove = [index for index, value in enumerate(ram_usage_list) if value < 2]
ram_usage_list = [value for index, value in enumerate(ram_usage_list) if index not in indices_to_remove]
cpu_percent_list = [value for index, value in enumerate(cpu_percent_list) if index not in indices_to_remove]


# Calculate average CPU and RAM utilization
average_cpu_utilization = sum(cpu_percent_list) / len(cpu_percent_list)
average_ram_utilization = sum(ram_usage_list) / len(ram_usage_list)


print(f"Average CPU Utilization: {average_cpu_utilization:.2f}%")
print("Min and Max CPU Utilization: ", min(cpu_percent_list), max(cpu_percent_list))
print(f"Average RAM Utilization: {average_ram_utilization:.2f} MB")
print("Min and Max RAM Utilization: ", min(ram_usage_list), max(ram_usage_list))
print(f"Total Execution Time: {execution_time:.2f} seconds")