import platform
import sys
import psutil

print("=" * 50)
print("     SYSTEM CONFIGURATION FOR RESEARCH REPORT     ")
print("=" * 50)

# 1. OS Info
print(f"Operating System : {platform.system()} {platform.release()} ({platform.architecture()[0]})")
print(f"OS Detail        : {platform.platform()}")

# 2. CPU Info
print(f"Processor (CPU)  : {platform.processor()}")
print(f"CPU Cores        : {psutil.cpu_count(logical=False)} Physical Cores, {psutil.cpu_count(logical=True)} Logical Threads")

# 3. RAM Info
ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
print(f"Total RAM        : {ram_gb} GB")

# 4. Software Versions
print(f"Python Version   : {sys.version.split()[0]}")

try:
    import pysat
    print(f"PySAT Version    : {pysat.__version__}")
except ImportError:
    print("PySAT Version    : Not installed")

try:
    import docplex
    print(f"DOcplex Version  : {docplex.__version__}")
except ImportError:
    print("DOcplex Version  : Not installed")

print("=" * 50)