import psutil
import time
import os

THRESHOLD = 75  # Auto-scaling trigger threshold

def create_gcp_vm():
    print("Deploying new VM on GCP...")
    os.system("gcloud compute instances create auto-scale-vm --machine-type=e2-medium --image-family=debian-11 --image-project=debian-cloud --zone=us-central1-a")

def check_resources():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    print(f"CPU Usage: {cpu_usage}%")
    print(f"Memory Usage: {memory_usage}%")

    with open("resource_log.txt", "a") as log_file:
        log_file.write(f"CPU: {cpu_usage}%, Memory: {memory_usage}%\n")

    if cpu_usage > THRESHOLD or memory_usage > THRESHOLD:
        print("High resource usage detected! Consider scaling up.")
        create_gcp_vm()

while True:
    check_resources()
    time.sleep(5)  # Run every 5 seconds
