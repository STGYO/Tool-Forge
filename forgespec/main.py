import platform
import psutil
import subprocess
import os
import sys

def get_os_info():
    """Collects operating system information."""
    print("\n--- Operating System ---")
    print(f"System: {platform.system()}")
    print(f"Node Name: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Architecture: {platform.architecture()}")

def get_cpu_info():
    """Collects CPU information."""
    print("\n--- CPU Information ---")
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    print(f"CPU usage: {psutil.cpu_percent(interval=1)}%") # Interval for a sample
    # Optional: Per-CPU usage
    # print("Per-CPU usage:")
    # for i, percentage in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
    #     print(f"  Core {i}: {percentage}%")
    print(f"CPU frequency: {psutil.cpu_freq().current:.2f} Mhz")

def get_ram_info():
    """Collects RAM information."""
    print("\n--- RAM Information ---")
    svmem = psutil.virtual_memory()
    print(f"Total: {svmem.total / (1024**3):.2f} GB")
    print(f"Available: {svmem.available / (1024**3):.2f} GB")
    print(f"Used: {svmem.used / (1024**3):.2f} GB")
    print(f"Percentage: {svmem.percent}%")

def get_disk_info():
    """Collects disk information."""
    print("\n--- Disk Information ---")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"--- Device: {partition.device} ---")
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Mountpoint: {partition.mountpoint}")
            print(f"  File system type: {partition.fstype}")
            print(f"  Total Size: {usage.total / (1024**3):.2f} GB")
            print(f"  Used: {usage.used / (1024**3):.2f} GB")
            print(f"  Free: {usage.free / (1024**3):.2f} GB")
            print(f"  Percentage: {usage.percent}%")
        except PermissionError:
            print(f"  Permission denied to access {partition.mountpoint}")
        except Exception as e:
            print(f"  Error accessing disk info for {partition.mountpoint}: {e}")

def get_gpu_info():
    """Attempts to collect basic GPU information (platform dependent)."""
    print("\n--- GPU Information (Basic) ---")
    if platform.system() == "Windows":
        try:
            # Using wmic for basic GPU info on Windows
            command = "wmic path win32_videocontroller get name"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                # Split lines and remove header/empty lines
                gpu_names = [line.strip() for line in result.stdout.splitlines() if line.strip() and "Name" not in line]
                if gpu_names:
                    print("GPU Name(s):")
                    for name in gpu_names:
                        print(f"  - {name}")
                else:
                    print("Could not retrieve GPU name using wmic.")
            else:
                print(f"Error running wmic command: {result.stderr.strip()}")
        except FileNotFoundError:
            print("wmic command not found. Cannot retrieve GPU info.")
        except Exception as e:
            print(f"An error occurred while getting Windows GPU info: {e}")
    elif platform.system() == "Darwin": # macOS
        try:
            # Using system_profiler for GPU info on macOS
            command = "system_profiler SPDisplaysDataType"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(result.stdout.strip()) # Print the full output
            else:
                print(f"Error running system_profiler command: {result.stderr.strip()}")
        except FileNotFoundError:
            print("system_profiler command not found. Cannot retrieve GPU info.")
        except Exception as e:
            print(f"An error occurred while getting macOS GPU info: {e}")
    elif platform.system() == "Linux":
        try:
            # Using lspci for GPU info on Linux (requires lspci to be installed)
            command = "lspci -vnn | grep -i VGA"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                 if result.stdout.strip():
                    print(result.stdout.strip())
                 else:
                    print("Could not find VGA compatible controller using lspci.")
            else:
                print(f"Error running lspci command: {result.stderr.strip()}")
        except FileNotFoundError:
            print("lspci command not found. Cannot retrieve GPU info.")
        except Exception as e:
            print(f"An error occurred while getting Linux GPU info: {e}")
    else:
        print(f"GPU information retrieval not implemented for {platform.system()}.")


if __name__ == "__main__":
    print("Generating system information snapshot...")
    get_os_info()
    get_cpu_info()
    get_ram_info()
    get_disk_info()
    get_gpu_info()
    print("\nSystem information snapshot complete.")
