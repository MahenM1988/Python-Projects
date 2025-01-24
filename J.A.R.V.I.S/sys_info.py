import subprocess
import GPUtil
import psutil
import platform

def get_processor_name():
    try:
        output = subprocess.check_output("wmic cpu get name", shell=True)
        return output.decode().split('\n')[1].strip()
    except Exception as e:
        return str(e)

def get_motherboard_name():
    try:
        output = subprocess.check_output("wmic baseboard get product, manufacturer", shell=True)
        lines = output.decode().strip().split('\n')
        if len(lines) > 1:
            return lines[1].strip()
        return "Unknown"
    except Exception as e:
        return str(e)

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].name
        else:
            output = subprocess.check_output("wmic path win32_VideoController get name", shell=True)
            lines = output.decode().strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
            return "Unknown"
    except Exception as e:
        return str(e)

def get_system_info():
    processor = get_processor_name()
    motherboard = get_motherboard_name()

    ram_info = psutil.virtual_memory()
    ram_total = ram_info.total / (1024 ** 3)  # Convert to GB

    disk_info = psutil.disk_usage('/')
    disk_total = disk_info.total / (1024 ** 3)  # Convert to GB

    gpu_name = get_gpu_info()

    os_info = platform.system() + " " + platform.release()

    return (processor, motherboard, ram_total, disk_total, gpu_name, os_info)