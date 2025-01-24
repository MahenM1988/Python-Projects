import pygame
import psutil
import GPUtil
import platform
import socket
import sys
import subprocess

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("System Resource Monitor")

# Set up fonts
font = pygame.font.Font(None, 36)
header_font = pygame.font.Font(None, 48)

def format_bytes(bytes):
    """Format bytes into GB, MB, or KB."""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024**2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes / 1024**2:.2f} MB"
    else:
        return f"{bytes / 1024**3:.2f} GB"

def get_processor_name():
    """Retrieve the processor name using subprocess (Windows)."""
    try:
        output = subprocess.check_output("wmic cpu get name", shell=True)
        return output.decode().split('\n')[1].strip()  # Get the second line (the actual name)
    except Exception as e:
        return str(e)

def get_motherboard_name():
    """Retrieve the motherboard name using subprocess (Windows)."""
    try:
        output = subprocess.check_output("wmic baseboard get product, manufacturer", shell=True)
        lines = output.decode().strip().split('\n')
        if len(lines) > 1:
            return lines[1].strip()  # Get the second line (the actual name and manufacturer)
        return "Unknown"
    except Exception as e:
        return str(e)

def get_gpu_info():
    """Retrieve GPU information."""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].name  # Return the name of the first detected GPU
        else:
            # Attempt to get integrated GPU info using wmic
            output = subprocess.check_output("wmic path win32_VideoController get name", shell=True)
            lines = output.decode().strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()  # Return the first line after the header
            return "Unknown"
    except Exception as e:
        return str(e)

def get_system_info():
    """Retrieve system information."""
    processor = get_processor_name()  # Get the full processor name
    motherboard = get_motherboard_name()  # Get the motherboard name
    
    ram_info = psutil.virtual_memory()
    ram_total = format_bytes(ram_info.total)
    ram_used = format_bytes(ram_info.used)
    ram_available = format_bytes(ram_info.available)
    
    disk_info = psutil.disk_usage('/')
    disk_total = format_bytes(disk_info.total)
    disk_used = format_bytes(disk_info.used)
    disk_available = format_bytes(disk_info.free)

    # Get GPU information
    gpu_name = get_gpu_info()  # Call the new GPU info function

    # Get OS information
    os_info = platform.system() + " " + platform.release()
    windows_version = platform.version() if platform.system() == "Windows" else "N/A"
    
    # Get IP Address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return (processor, motherboard, ram_total, ram_used, ram_available, 
            disk_total, disk_used, disk_available, gpu_name, 
            os_info, windows_version, ip_address)

def get_usage_data():
    """Retrieve system resource usage."""
    cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    
    # Get network usage
    network_info = psutil.net_io_counters()
    network_sent = network_info.bytes_sent
    network_recv = network_info.bytes_recv

    return cpu_usage_per_core, memory_usage, network_sent, network_recv

# Main loop
running = True
previous_network_info = psutil.net_io_counters()  # Initial network stats

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get system information
    (processor, motherboard, ram_total, ram_used, ram_available, 
     disk_total, disk_used, disk_available, gpu_name, 
     os_info, windows_version, ip_address) = get_system_info()
    
    # Get usage data
    cpu_usage_per_core, memory, network_sent, network_recv = get_usage_data()

    # Clear the screen with a black background
    screen.fill((0, 0, 0))  # Set to black

    # Render header
    header_text = header_font.render("System Resource Monitor", True, (255, 0, 0))  # Red text
    screen.blit(header_text, (20, 20))

    # Render System Info
    y_offset = 80
    spacing = 50  # Space between each section

    info_texts = [
        f"Processor: {processor}",
        f"Motherboard: {motherboard}",
        f"RAM: Total: {ram_total}, Used: {ram_used}, Available: {ram_available}",
        f"Disk: Total: {disk_total}, Used: {disk_used}, Available: {disk_available}",
        f"GPU: {gpu_name}",
        f"OS: {os_info}",
        f"Windows Version: {windows_version}",
        f"IP Address: {ip_address}",
        "",  # Extra space after IP Address
    ]

    for text in info_texts:
        info_render = font.render(text, True, (255, 0, 0))  # Red text
        screen.blit(info_render, (20, y_offset))
        y_offset += 30

    # Render CPU usage
    cpu_text = font.render("CPU Cores Usage:", True, (255, 0, 0))  # Red text
    screen.blit(cpu_text, (20, y_offset))
    y_offset += 30

    for i, usage in enumerate(cpu_usage_per_core):
        core_text = font.render(f"Core {i}: {usage}%", True, (255, 0, 0))  # Red text
        screen.blit(core_text, (40, y_offset))
        y_offset += 30

    y_offset += 20  # Extra space before Memory Usage

    # Render Memory Usage Percentage
    memory_text = font.render(f"Memory Usage: {memory}%", True, (255, 0, 0))  # Red text
    screen.blit(memory_text, (20, y_offset))
    y_offset += spacing  # Extra space before network stats

    # Calculate and render Network Usage
    current_network_info = psutil.net_io_counters()
    sent_per_sec = current_network_info.bytes_sent - previous_network_info.bytes_sent
    recv_per_sec = current_network_info.bytes_recv - previous_network_info.bytes_recv

    network_sent_per_sec = format_bytes(sent_per_sec)
    network_recv_per_sec = format_bytes(recv_per_sec)

    network_sent_text = font.render(f"Network Sent: {network_sent_per_sec}/s", True, (255, 0, 0))  # Red text
    network_recv_text = font.render(f"Network Received: {network_recv_per_sec}/s", True, (255, 0, 0))  # Red text

    screen.blit(network_sent_text, (20, y_offset))
    y_offset += 30
    screen.blit(network_recv_text, (20, y_offset))
    y_offset += 30

    # Update previous network stats for next calculation
    previous_network_info = current_network_info

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.delay(1000)  # Update every second

# Quit Pygame
pygame.quit()
sys.exit()
