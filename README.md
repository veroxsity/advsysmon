# Advanced System Monitor

A feature-rich, modern system monitor with a beautiful terminal UI built using Python and Rich.

## Features

### 🖥️ **Comprehensive System Information**
- Hostname, OS, architecture, processor details
- Python version and system uptime
- Boot time information

### 📊 **CPU Monitoring**
- Real-time CPU usage with visual progress bars
- Per-core CPU information
- CPU frequency monitoring
- Temperature monitoring (when available)
- Load average (1min, 5min, 15min)
- Historical usage sparklines

### 💾 **Memory Monitoring**
- RAM usage with detailed breakdown
- Swap memory monitoring
- Available, buffers, and cached memory
- Memory usage history visualization

### 💿 **Disk Monitoring**
- Multiple disk partition monitoring
- Usage statistics for all mounted drives
- File system information
- Visual usage indicators

### 🌐 **Network Monitoring**
- Real-time upload/download speeds
- Total data transferred
- Active network interfaces
- Network activity history

### 🔋 **Battery Monitoring**
- Battery percentage and status
- Charging/discharging indication
- Time remaining estimation
- Visual battery level indicator

### 🎮 **GPU Monitoring** (if available)
- GPU usage and memory
- Temperature monitoring
- Multiple GPU support

### 🔄 **Process Monitoring**
- Top 10 processes by CPU usage
- Process ID, name, CPU%, memory usage
- Real-time process information

### 🎨 **Modern UI Features**
- Beautiful terminal interface using Rich
- Color-coded progress bars
- Real-time sparkline graphs
- Responsive layout
- Clean, organized panels

## Installation

### Quick Install from GitHub

```bash
# Clone the repository
git clone https://github.com/veroxsity/advsysmon.git
cd advsysmon

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 src/advsysmon.py
```

### Alternative: Direct Download

```bash
# Download just the main script
curl -O https://raw.githubusercontent.com/veroxsity/advsysmon/main/src/advsysmon.py

# Install dependencies manually
pip3 install psutil rich colorama tabulate blessed click

# Optional GPU monitoring dependencies
pip3 install pynvml GPUtil

# Run the application
python3 advsysmon.py
```
advanced-sysmon
```

## Requirements

- Python 3.7+
- Linux/macOS/Windows
- Terminal with color support

## Optional Dependencies

- **pynvml/GPUtil**: For GPU monitoring
- Modern terminal emulator for best visual experience

## Usage

Simply run the script and enjoy the real-time system monitoring:

```bash
python3 src/advsysmon.py
```

Press `Ctrl+C` to exit gracefully.

## Features Overview

The monitor displays information in organized panels:

1. **System Information**: Static system details
2. **CPU Information**: Real-time CPU metrics
3. **Memory Information**: RAM and swap usage
4. **Disk Usage**: Storage information for all drives
5. **Network Information**: Network speeds and statistics
6. **Battery**: Power status (if available)
7. **GPU Information**: Graphics card stats (if available)
8. **Top Processes**: Most resource-intensive processes

All panels update in real-time and include visual indicators like progress bars and historical data sparklines.

## Compatibility

- ✅ Linux (full feature support)
- ✅ macOS (most features)
- ✅ Windows (most features)
- ⚠️ Some features like temperature monitoring may not be available on all systems

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this system monitor!

## Author

Created by Daniel ([@veroxsity](https://github.com/veroxsity))

## Repository

https://github.com/veroxsity/advsysmon
