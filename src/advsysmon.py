#!/usr/bin/env python3
"""
Advanced System Monitor with Rich UI
Author: Daniel (@veroxsity)
Email: veroxsity@gmail.com
Repository: https://github.com/veroxsity/advsysmon
Date: July 2025
"""

import os
import sys
import time
import platform
import socket
from datetime import datetime, timedelta
from collections import deque
import threading
import signal

import psutil
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.align import Align

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class SystemMonitor:
    def __init__(self):
        self.console = Console()
        self.running = True
        self.update_interval = 1.0
        
        # Historical data for graphs
        self.cpu_history = deque(maxlen=50)
        self.memory_history = deque(maxlen=50)
        self.network_history = deque(maxlen=50)
        
        # Previous network counters for speed calculation
        self.prev_net_counters = self._get_net_counters()
        
        # Process monitoring
        self.process_sort_key = 'cpu_percent'
        self.show_processes = True
        
        # System info cache
        self.system_info = self._get_system_info()
        
    def _get_system_info(self):
        """Get static system information"""
        uname = platform.uname()
        return {
            'system': uname.system,
            'node': uname.node,
            'release': uname.release,
            'version': uname.version,
            'machine': uname.machine,
            'processor': uname.processor or 'Unknown',
            'python_version': platform.python_version(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time())
        }
    
    def _get_net_counters(self):
        """Get current network counters"""
        try:
            counters = psutil.net_io_counters()
            return counters.bytes_sent, counters.bytes_recv
        except:
            return 0, 0
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
            
        return f"{bytes_value:.1f} {units[unit_index]}"
    
    def _format_frequency(self, freq_mhz):
        """Format frequency from MHz to human readable"""
        if freq_mhz >= 1000:
            return f"{freq_mhz/1000:.1f} GHz"
        return f"{freq_mhz:.0f} MHz"
    
    def _get_cpu_info(self):
        """Get comprehensive CPU information"""
        cpu_info = {}
        
        # Basic CPU stats
        cpu_info['usage'] = psutil.cpu_percent(interval=None)
        cpu_info['count_logical'] = psutil.cpu_count(logical=True)
        cpu_info['count_physical'] = psutil.cpu_count(logical=False)
        
        # Per-core usage
        cpu_info['per_core'] = psutil.cpu_percent(interval=None, percpu=True)
        
        # CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_info['current_freq'] = freq.current
                cpu_info['min_freq'] = freq.min
                cpu_info['max_freq'] = freq.max
        except:
            pass
            
        # CPU temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_info['temperature'] = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:
                cpu_info['temperature'] = temps['cpu_thermal'][0].current
        except:
            pass
            
        # Load average
        try:
            cpu_info['load_avg'] = os.getloadavg()
        except:
            pass
            
        return cpu_info
    
    def _get_memory_info(self):
        """Get memory information"""
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'virtual': virtual,
            'swap': swap,
            'virtual_used_gb': virtual.used / (1024**3),
            'virtual_total_gb': virtual.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_total_gb': swap.total / (1024**3),
        }
    
    def _get_disk_info(self):
        """Get disk usage information for all mounted disks"""
        disks = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                })
            except PermissionError:
                continue
                
        return disks
    
    def _get_network_info(self):
        """Get network information and calculate speeds"""
        current_counters = self._get_net_counters()
        
        # Calculate speeds
        upload_speed = (current_counters[0] - self.prev_net_counters[0]) / self.update_interval
        download_speed = (current_counters[1] - self.prev_net_counters[1]) / self.update_interval
        
        self.prev_net_counters = current_counters
        
        # Get network interfaces
        interfaces = []
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                ip_addresses = [addr.address for addr in addresses if addr.family == socket.AF_INET]
                
                interfaces.append({
                    'name': interface_name,
                    'is_up': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu,
                    'ip_addresses': ip_addresses
                })
        
        return {
            'upload_speed': upload_speed,
            'download_speed': download_speed,
            'total_sent': current_counters[0],
            'total_recv': current_counters[1],
            'interfaces': interfaces
        }
    
    def _get_gpu_info(self):
        """Get GPU information if available"""
        if not GPU_AVAILABLE:
            return None
            
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []
            
            for gpu in gpus:
                gpu_info.append({
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                    'temperature': gpu.temperature
                })
                
            return gpu_info
        except:
            return None
    
    def _get_battery_info(self):
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except:
            pass
        return None
    
    def _get_top_processes(self, limit=10):
        """Get top processes by CPU or memory usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by the selected key
        processes.sort(key=lambda x: x.get(self.process_sort_key, 0), reverse=True)
        return processes[:limit]
    
    def _create_progress_bar(self, percentage, width=20):
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color coding
        if percentage > 90:
            color = "red"
        elif percentage > 70:
            color = "yellow"
        else:
            color = "green"
            
        return Text(f"{bar} {percentage:5.1f}%", style=color)
    
    def _create_sparkline(self, data, width=20):
        """Create a simple sparkline from data"""
        if not data or len(data) < 2:
            return "No data"
            
        # Normalize data to 0-7 range for Unicode block characters
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return "▄" * width
            
        blocks = "▁▂▃▄▅▆▇█"
        normalized = [(val - min_val) / (max_val - min_val) * 7 for val in data[-width:]]
        
        sparkline = ""
        for val in normalized:
            sparkline += blocks[int(val)]
            
        return sparkline
    
    def _create_system_info_panel(self):
        """Create system information panel"""
        info = self.system_info
        uptime = datetime.now() - info['boot_time']
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Label", style="cyan")
        table.add_column("Value")
        
        table.add_row("Hostname", info['node'])
        table.add_row("OS", f"{info['system']} {info['release']}")
        table.add_row("Architecture", info['machine'])
        table.add_row("Processor", info['processor'])
        table.add_row("Python", info['python_version'])
        table.add_row("Uptime", str(uptime).split('.')[0])
        table.add_row("Boot Time", info['boot_time'].strftime("%Y-%m-%d %H:%M:%S"))
        
        return Panel(table, title="System Information", border_style="blue")
    
    def _create_cpu_panel(self):
        """Create CPU information panel"""
        cpu_info = self._get_cpu_info()
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_column("Visual")
        
        # Overall CPU usage
        table.add_row(
            "CPU Usage",
            f"{cpu_info['usage']:.1f}%",
            self._create_progress_bar(cpu_info['usage'])
        )
        
        # CPU cores
        table.add_row(
            "Cores",
            f"{cpu_info['count_physical']} physical, {cpu_info['count_logical']} logical",
            ""
        )
        
        # Frequency
        if 'current_freq' in cpu_info:
            table.add_row(
                "Frequency",
                f"{self._format_frequency(cpu_info['current_freq'])}",
                f"Max: {self._format_frequency(cpu_info['max_freq'])}"
            )
        
        # Temperature
        if 'temperature' in cpu_info:
            temp_color = "green" if cpu_info['temperature'] < 70 else "yellow" if cpu_info['temperature'] < 85 else "red"
            table.add_row(
                "Temperature",
                f"{cpu_info['temperature']:.1f}°C",
                Text("", style=temp_color)
            )
        
        # Load average
        if 'load_avg' in cpu_info:
            load_1, load_5, load_15 = cpu_info['load_avg']
            table.add_row(
                "Load Avg",
                f"{load_1:.2f}, {load_5:.2f}, {load_15:.2f}",
                ""
            )
        
        # History sparkline
        self.cpu_history.append(cpu_info['usage'])
        table.add_row(
            "History",
            self._create_sparkline(list(self.cpu_history)),
            ""
        )
        
        return Panel(table, title="CPU Information", border_style="red")
    
    def _create_memory_panel(self):
        """Create memory information panel"""
        mem_info = self._get_memory_info()
        virtual = mem_info['virtual']
        swap = mem_info['swap']
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Type", style="cyan")
        table.add_column("Usage")
        table.add_column("Visual")
        
        # Virtual memory
        table.add_row(
            "RAM",
            f"{self._format_bytes(virtual.used)} / {self._format_bytes(virtual.total)}",
            self._create_progress_bar(virtual.percent)
        )
        
        # Swap memory
        if swap.total > 0:
            table.add_row(
                "Swap",
                f"{self._format_bytes(swap.used)} / {self._format_bytes(swap.total)}",
                self._create_progress_bar(swap.percent)
            )
        
        # Memory breakdown
        table.add_row("Available", self._format_bytes(virtual.available), "")
        if hasattr(virtual, 'buffers'):
            table.add_row("Buffers", self._format_bytes(virtual.buffers), "")
        if hasattr(virtual, 'cached'):
            table.add_row("Cached", self._format_bytes(virtual.cached), "")
        
        # History
        self.memory_history.append(virtual.percent)
        table.add_row(
            "History",
            self._create_sparkline(list(self.memory_history)),
            ""
        )
        
        return Panel(table, title="Memory Information", border_style="green")
    
    def _create_disk_panel(self):
        """Create disk information panel"""
        disks = self._get_disk_info()
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Device", style="cyan")
        table.add_column("Mount Point")
        table.add_column("File System")
        table.add_column("Used")
        table.add_column("Total")
        table.add_column("Usage")
        
        for disk in disks[:5]:  # Show top 5 disks
            usage_bar = self._create_progress_bar(disk['percent'], width=15)
            table.add_row(
                disk['device'],
                disk['mountpoint'],
                disk['fstype'],
                self._format_bytes(disk['used']),
                self._format_bytes(disk['total']),
                usage_bar
            )
        
        return Panel(table, title="Disk Usage", border_style="yellow")
    
    def _create_network_panel(self):
        """Create network information panel"""
        net_info = self._get_network_info()
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_column("Visual")
        
        # Current speeds
        table.add_row(
            "Download",
            f"{self._format_bytes(net_info['download_speed'])}/s",
            ""
        )
        table.add_row(
            "Upload",
            f"{self._format_bytes(net_info['upload_speed'])}/s",
            ""
        )
        
        # Total transferred
        table.add_row(
            "Total Received",
            self._format_bytes(net_info['total_recv']),
            ""
        )
        table.add_row(
            "Total Sent",
            self._format_bytes(net_info['total_sent']),
            ""
        )
        
        # Active interfaces
        active_interfaces = [iface for iface in net_info['interfaces'] if iface['is_up']]
        table.add_row(
            "Active Interfaces",
            f"{len(active_interfaces)} up",
            ""
        )
        
        # Network history
        total_speed = net_info['download_speed'] + net_info['upload_speed']
        self.network_history.append(total_speed / 1024)  # Convert to KB/s
        table.add_row(
            "Activity",
            self._create_sparkline(list(self.network_history)),
            ""
        )
        
        return Panel(table, title="Network Information", border_style="blue")
    
    def _create_gpu_panel(self):
        """Create GPU information panel"""
        gpu_info = self._get_gpu_info()
        
        if not gpu_info:
            return Panel(
                Align.center("No GPU detected or GPUtil not available"),
                title="GPU Information",
                border_style="dim"
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("GPU", style="cyan")
        table.add_column("Load")
        table.add_column("Memory")
        table.add_column("Temperature")
        
        for gpu in gpu_info:
            table.add_row(
                gpu['name'],
                self._create_progress_bar(gpu['load'], width=10),
                f"{gpu['memory_used']}MB / {gpu['memory_total']}MB",
                f"{gpu['temperature']}°C"
            )
        
        return Panel(table, title="GPU Information", border_style="magenta")
    
    def _create_battery_panel(self):
        """Create battery information panel"""
        battery_info = self._get_battery_info()
        
        if not battery_info:
            return Panel(
                Align.center("No battery detected"),
                title="Battery",
                border_style="dim"
            )
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_column("Visual")
        
        status = "🔌 Charging" if battery_info['plugged'] else "🔋 Discharging"
        table.add_row("Status", status, "")
        
        table.add_row(
            "Charge",
            f"{battery_info['percent']:.1f}%",
            self._create_progress_bar(battery_info['percent'])
        )
        
        if battery_info['time_left']:
            time_left = str(timedelta(seconds=battery_info['time_left']))
            table.add_row("Time Left", time_left, "")
        
        return Panel(table, title="Battery", border_style="cyan")
    
    def _create_processes_panel(self):
        """Create top processes panel"""
        processes = self._get_top_processes()
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("PID", justify="right")
        table.add_column("Name", style="cyan")
        table.add_column("CPU%", justify="right")
        table.add_column("Memory%", justify="right")
        table.add_column("Memory", justify="right")
        
        for proc in processes:
            memory_info = proc.get('memory_info')
            memory_mb = 0
            if memory_info and hasattr(memory_info, 'rss'):
                memory_mb = memory_info.rss / (1024 * 1024)
            elif isinstance(memory_info, dict) and 'rss' in memory_info:
                memory_mb = memory_info['rss'] / (1024 * 1024)
            
            table.add_row(
                str(proc['pid']),
                proc['name'][:20],
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_percent']:.1f}",
                f"{memory_mb:.0f}MB"
            )
        
        return Panel(table, title="Top Processes (by CPU)", border_style="white")
    
    def create_layout(self):
        """Create the main layout"""
        layout = Layout()
        
        # Split into header and body
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header with title and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_text = Text.assemble(
            ("🖥️  Advanced System Monitor", "bold blue"),
            " | ",
            (f"Updated: {timestamp}", "dim")
        )
        layout["header"].update(Panel(Align.center(header_text), border_style="bright_blue"))
        
        # Split body into left and right columns
        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Split left column into rows
        layout["left"].split_column(
            Layout(name="system_cpu", ratio=1),
            Layout(name="memory_disk", ratio=1),
            Layout(name="network_battery", ratio=1)
        )
        
        # Split system_cpu row
        layout["system_cpu"].split_row(
            Layout(self._create_system_info_panel()),
            Layout(self._create_cpu_panel())
        )
        
        # Split memory_disk row
        layout["memory_disk"].split_row(
            Layout(self._create_memory_panel()),
            Layout(self._create_disk_panel())
        )
        
        # Split network_battery row
        network_battery_panels = [self._create_network_panel()]
        
        # Add battery panel if available
        battery_panel = self._create_battery_panel()
        if "No battery detected" not in str(battery_panel):
            network_battery_panels.append(battery_panel)
        
        # Add GPU panel if available
        gpu_panel = self._create_gpu_panel()
        if "No GPU detected" not in str(gpu_panel):
            network_battery_panels.append(gpu_panel)
        
        if len(network_battery_panels) == 1:
            layout["network_battery"].update(network_battery_panels[0])
        elif len(network_battery_panels) == 2:
            layout["network_battery"].split_row(*network_battery_panels)
        else:
            layout["network_battery"].split_column(*network_battery_panels)
        
        # Right column for processes
        layout["right"].update(self._create_processes_panel())
        
        return layout
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.running = False
        self.console.print("\n[yellow]Shutting down system monitor...[/yellow]")
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            with Live(self.create_layout(), refresh_per_second=1, screen=True) as live:
                while self.running:
                    time.sleep(self.update_interval)
                    live.update(self.create_layout())
        except KeyboardInterrupt:
            self.signal_handler(None, None)

def main():
    """Main entry point"""
    monitor = SystemMonitor()
    
    # Check if running in a terminal
    if not os.isatty(sys.stdout.fileno()):
        print("This application requires a terminal to run properly.")
        sys.exit(1)
    
    try:
        monitor.run()
    except Exception as e:
        print(f"Error starting system monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
