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

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the monitor:
```bash
python sysmon.py
```

## Quick Install (Debian/Ubuntu)

```bash
# Download and install the .deb package
wget https://github.com/veroxsity/advsysmon/releases/latest/download/advanced-sysmon.deb
sudo dpkg -i advanced-sysmon.deb

# Run the application
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
python sysmon.py
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
