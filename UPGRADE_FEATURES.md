# Advanced System Monitor - New Features

## 🎉 Major Upgrades

Your system monitor has been significantly enhanced with powerful new features:

### 🚀 **Enhanced Monitoring**
- **Per-core CPU monitoring** - See individual CPU core usage
- **Advanced temperature monitoring** - Color-coded temperature alerts with emoji indicators
- **Disk I/O monitoring** - Real-time read/write speeds
- **Network connection tracking** - Monitor active connections and status
- **Extended history graphs** - Longer sparkline charts (100 data points)

### 🐳 **Docker Integration**
- **Container monitoring** - View running containers, images, and status
- **Resource usage** - Monitor container CPU and memory usage
- **Port mapping display** - See exposed container ports
- *Note: Requires `pip install docker` for full functionality*

### ⚠️ **Smart Alerting System**
- **Configurable thresholds** - Set custom warning and critical levels
- **Real-time alerts** - Visual indicators for system issues
- **Alert history** - Track recent alerts with timestamps
- **Multi-level alerts** - Warning (yellow) and critical (red) notifications

### 🎛️ **Interactive Controls**
- **Multiple view modes** - Main dashboard, Docker view, Alerts view
- **Keyboard shortcuts** - Easy navigation and control
- **Toggle panels** - Show/hide individual monitoring panels
- **Sorting options** - Sort processes by CPU, memory, PID, or name
- **Adjustable update rates** - Change refresh intervals on the fly

### ⚙️ **Configuration System**
- **Persistent settings** - Automatically saves preferences
- **JSON configuration** - Easy to edit configuration file
- **Custom thresholds** - Set your own alert levels
- **Panel visibility** - Choose which panels to display

### 🎨 **UI Improvements**
- **Enhanced color coding** - Better visual feedback for system status
- **Improved layouts** - More efficient use of screen space
- **Progress bars** - Visual indicators for resource usage
- **Status indicators** - Emoji-based quick status recognition
- **Truncated display** - Better handling of long names and paths

## 🎮 **Keyboard Controls**

### Navigation
- `q` - Quit application
- `h` - Toggle help panel
- `1` - Main dashboard view
- `2` - Docker containers view
- `3` - System alerts view

### Process Management
- `c` - Sort processes by CPU usage
- `m` - Sort processes by Memory usage
- `p` - Sort processes by PID
- `n` - Sort processes by Name

### Panel Toggles
- `s` - Toggle system info panel
- `u` - Toggle CPU panel
- `r` - Toggle memory panel
- `d` - Toggle disk panel
- `t` - Toggle network panel
- `g` - Toggle GPU panel
- `b` - Toggle battery panel

### Settings
- `+` - Increase update interval
- `-` - Decrease update interval

## 📁 **Configuration**

Settings are automatically saved to `~/.config/advsysmon/config.json`. You can manually edit this file to customize:

- Update intervals
- Alert thresholds
- Panel visibility
- Default process sorting

## 🔧 **Optional Dependencies**

For full functionality, install these optional packages:

```bash
# For GPU monitoring
pip install GPUtil

# For Docker monitoring
pip install docker

# For enhanced terminal features
pip install blessed
```

## 🚀 **Quick Start**

1. Use the launcher script: `./start_monitor.sh`
2. Or run directly: `python3 src/advsysmon.py`
3. Press `h` for help once started
4. Use number keys (1, 2, 3) to switch between views
5. Use letter keys to toggle panels and sort processes

## 🎯 **System Requirements**

- Python 3.6+
- Linux/Unix terminal with color support
- psutil and rich libraries (automatically installed)
- Optional: Docker daemon for container monitoring
- Optional: NVIDIA GPU for GPU monitoring

Enjoy your upgraded system monitor! 🚀
