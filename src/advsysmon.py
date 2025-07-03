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
import json
import subprocess
from datetime import datetime, timedelta
from collections import deque
import threading
import signal
from pathlib import Path

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
from rich.status import Status
from rich.tree import Tree

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

class SystemMonitor:
    def __init__(self):
        self.console = Console()
        self.running = True
        self.update_interval = 1.0
        
        # Configuration
        self.config_file = Path.home() / ".config" / "advsysmon" / "config.json"
        self.config = self._load_config()
        
        # UI State
        self.current_view = "main"  # main, processes, docker, network, logs
        self.process_sort_key = self.config.get('process_sort_key', 'cpu_percent')
        self.show_processes = True
        self.selected_process_index = 0
        self.show_help = False
        
        # Monitoring toggles
        self.show_system_info = self.config.get('show_system_info', True)
        self.show_cpu = self.config.get('show_cpu', True)
        self.show_memory = self.config.get('show_memory', True)
        self.show_disk = self.config.get('show_disk', True)
        self.show_network = self.config.get('show_network', True)
        self.show_gpu = self.config.get('show_gpu', True)
        self.show_battery = self.config.get('show_battery', True)
        
        # Historical data for graphs
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.network_history = deque(maxlen=100)
        self.disk_io_history = deque(maxlen=100)
        
        # Previous counters for delta calculations
        self.prev_net_counters = self._get_net_counters()
        self.prev_disk_counters = self._get_disk_io_counters()
        
        # System info cache
        self.system_info = self._get_system_info()
        
        # Alerts and thresholds
        self.alerts = []
        self.thresholds = self.config.get('thresholds', {
            'cpu_warning': 80,
            'cpu_critical': 95,
            'memory_warning': 80,
            'memory_critical': 95,
            'disk_warning': 85,
            'disk_critical': 95,
            'temperature_warning': 75,
            'temperature_critical': 85
        })
        
        # Docker monitoring
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
            except:
                pass
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return self._default_config()
    
    def _default_config(self):
        """Default configuration"""
        return {
            'update_interval': 1.0,
            'process_sort_key': 'cpu_percent',
            'show_system_info': True,
            'show_cpu': True,
            'show_memory': True,
            'show_disk': True,
            'show_network': True,
            'show_gpu': True,
            'show_battery': True,
            'thresholds': {
                'cpu_warning': 80,
                'cpu_critical': 95,
                'memory_warning': 80,
                'memory_critical': 95,
                'disk_warning': 85,
                'disk_critical': 95,
                'temperature_warning': 75,
                'temperature_critical': 85
            }
        }
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                'update_interval': self.update_interval,
                'process_sort_key': self.process_sort_key,
                'show_system_info': self.show_system_info,
                'show_cpu': self.show_cpu,
                'show_memory': self.show_memory,
                'show_disk': self.show_disk,
                'show_network': self.show_network,
                'show_gpu': self.show_gpu,
                'show_battery': self.show_battery,
                'thresholds': self.thresholds
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
        
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
    
    def _get_disk_io_counters(self):
        """Get current disk I/O counters"""
        try:
            counters = psutil.disk_io_counters()
            return counters.read_bytes, counters.write_bytes
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
    
    def _check_alerts(self):
        """Check system metrics against thresholds and generate alerts"""
        current_time = datetime.now()
        
        # CPU alert
        cpu_usage = psutil.cpu_percent(interval=None)
        if cpu_usage > self.thresholds['cpu_critical']:
            self.alerts.append({
                'time': current_time,
                'level': 'critical',
                'message': f'Critical CPU usage: {cpu_usage:.1f}%',
                'metric': 'cpu'
            })
        elif cpu_usage > self.thresholds['cpu_warning']:
            self.alerts.append({
                'time': current_time,
                'level': 'warning',
                'message': f'High CPU usage: {cpu_usage:.1f}%',
                'metric': 'cpu'
            })
        
        # Memory alert
        memory = psutil.virtual_memory()
        if memory.percent > self.thresholds['memory_critical']:
            self.alerts.append({
                'time': current_time,
                'level': 'critical',
                'message': f'Critical memory usage: {memory.percent:.1f}%',
                'metric': 'memory'
            })
        elif memory.percent > self.thresholds['memory_warning']:
            self.alerts.append({
                'time': current_time,
                'level': 'warning',
                'message': f'High memory usage: {memory.percent:.1f}%',
                'metric': 'memory'
            })
        
        # Keep only last 10 alerts
        self.alerts = self.alerts[-10:]
    
    def _get_docker_info(self):
        """Get Docker container information"""
        if not self.docker_client:
            return None
        
        try:
            containers = self.docker_client.containers.list(all=True)
            container_info = []
            
            for container in containers:
                stats = None
                if container.status == 'running':
                    try:
                        stats = container.stats(stream=False)
                    except:
                        pass
                
                container_info.append({
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'status': container.status,
                    'ports': container.ports,
                    'stats': stats
                })
            
            return container_info
        except:
            return None
    
    def _get_system_services(self):
        """Get system services status"""
        services = []
        try:
            # Get systemd services
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager', '--no-legend'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            services.append({
                                'name': parts[0].replace('.service', ''),
                                'status': parts[2],
                                'description': ' '.join(parts[4:])
                            })
        except:
            pass
        
        return services[:20]  # Limit to 20 services
    
    def _get_network_connections(self):
        """Get active network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            connection_summary = {
                'established': 0,
                'listen': 0,
                'time_wait': 0,
                'close_wait': 0,
                'syn_sent': 0,
                'syn_recv': 0
            }
            
            for conn in connections:
                status = conn.status.lower() if conn.status else 'unknown'
                if status in connection_summary:
                    connection_summary[status] += 1
                    
            return connection_summary
        except:
            return {}
    
    def create_layout(self):
        """Create the main layout"""
        # Check for alerts
        self._check_alerts()
        
        layout = Layout()
        
        # Split into header and body
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header with title, timestamp, and view indicator
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_indicator = ""
        if self.alerts:
            recent_critical = any(a['level'] == 'critical' for a in self.alerts[-3:])
            alert_indicator = " 🔴 CRITICAL ALERTS" if recent_critical else " ⚠️ ALERTS"
        
        header_text = Text.assemble(
            ("🖥️  Advanced System Monitor", "bold blue"),
            (alert_indicator, "bold red" if "CRITICAL" in alert_indicator else "bold yellow"),
            " | ",
            (f"Updated: {timestamp}", "dim"),
            " | ",
            (f"View: {self.current_view.upper()}", "bold green")
        )
        layout["header"].update(Panel(Align.center(header_text), border_style="bright_blue"))
        
        if self.current_view == "main":
            # Main dashboard view
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
            if self.show_system_info and self.show_cpu:
                layout["system_cpu"].split_row(
                    Layout(self._create_system_info_panel()),
                    Layout(self._create_cpu_panel())
                )
            elif self.show_system_info:
                layout["system_cpu"].update(self._create_system_info_panel())
            elif self.show_cpu:
                layout["system_cpu"].update(self._create_cpu_panel())
            
            # Split memory_disk row
            if self.show_memory and self.show_disk:
                layout["memory_disk"].split_row(
                    Layout(self._create_memory_panel()),
                    Layout(self._create_disk_panel())
                )
            elif self.show_memory:
                layout["memory_disk"].update(self._create_memory_panel())
            elif self.show_disk:
                layout["memory_disk"].update(self._create_disk_panel())
            
            # Split network_battery row
            network_battery_panels = []
            if self.show_network:
                network_battery_panels.append(self._create_network_panel())
            
            # Add battery panel if available and enabled
            if self.show_battery:
                battery_panel = self._create_battery_panel()
                if "No battery detected" not in str(battery_panel):
                    network_battery_panels.append(battery_panel)
            
            # Add GPU panel if available and enabled
            if self.show_gpu:
                gpu_panel = self._create_gpu_panel()
                if "No GPU detected" not in str(gpu_panel):
                    network_battery_panels.append(gpu_panel)
            
            if len(network_battery_panels) == 1:
                layout["network_battery"].update(network_battery_panels[0])
            elif len(network_battery_panels) == 2:
                layout["network_battery"].split_row(*network_battery_panels)
            elif len(network_battery_panels) >= 3:
                layout["network_battery"].split_column(*network_battery_panels[:3])
            
            # Right column for processes or alerts
            if self.alerts and len(self.alerts) > 3:
                layout["right"].split_column(
                    Layout(self._create_alerts_panel(), ratio=1),
                    Layout(self._create_processes_panel(), ratio=2)
                )
            else:
                layout["right"].update(self._create_processes_panel())
        
        elif self.current_view == "docker":
            # Docker view
            layout["body"].split_column(
                Layout(self._create_docker_panel(), ratio=2),
                Layout(self._create_services_panel(), ratio=1)
            )
        
        elif self.current_view == "alerts":
            # Alerts view
            layout["body"].split_column(
                Layout(self._create_alerts_panel(), ratio=1),
                Layout(self._create_system_info_panel(), ratio=1)
            )
        
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
        
        # Add alerts indicator
        if self.alerts:
            recent_alerts = len([a for a in self.alerts if (datetime.now() - a['time']).seconds < 300])
            alert_color = "red" if any(a['level'] == 'critical' for a in self.alerts[-3:]) else "yellow"
            table.add_row("⚠️ Alerts", f"{recent_alerts} recent", Text("", style=alert_color))
        
        return Panel(table, title="System Information", border_style="blue")
    
    def _create_cpu_panel(self):
        """Create CPU information panel with enhanced monitoring"""
        cpu_info = self._get_cpu_info()
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_column("Visual")
        
        # Overall CPU usage with alert coloring
        cpu_color = "green"
        if cpu_info['usage'] > self.thresholds['cpu_critical']:
            cpu_color = "red"
        elif cpu_info['usage'] > self.thresholds['cpu_warning']:
            cpu_color = "yellow"
        
        table.add_row(
            "CPU Usage",
            f"{cpu_info['usage']:.1f}%",
            self._create_progress_bar(cpu_info['usage'])
        )
        
        # Per-core usage (show first 8 cores)
        if 'per_core' in cpu_info and len(cpu_info['per_core']) > 1:
            cores_to_show = min(8, len(cpu_info['per_core']))
            core_usage_text = []
            for i in range(cores_to_show):
                core_usage = cpu_info['per_core'][i]
                core_usage_text.append(f"C{i}: {core_usage:.0f}%")
            
            # Split cores into two columns
            for i in range(0, len(core_usage_text), 2):
                left_core = core_usage_text[i]
                right_core = core_usage_text[i+1] if i+1 < len(core_usage_text) else ""
                if i == 0:
                    table.add_row("Per Core", left_core, right_core)
                else:
                    table.add_row("", left_core, right_core)
        
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
        
        # Temperature with enhanced monitoring
        if 'temperature' in cpu_info:
            temp = cpu_info['temperature']
            temp_icon = "🟢"
            if temp > self.thresholds['temperature_critical']:
                temp_icon = "🔴"
            elif temp > self.thresholds['temperature_warning']:
                temp_icon = "🟡"
            
            table.add_row(
                "Temperature",
                f"{temp:.1f}°C {temp_icon}",
                ""
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
            self._create_sparkline(list(self.cpu_history), width=30),
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
        
        # Virtual memory with alert coloring
        memory_color = "green"
        if virtual.percent > self.thresholds['memory_critical']:
            memory_color = "red"
        elif virtual.percent > self.thresholds['memory_warning']:
            memory_color = "yellow"
        
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
            self._create_sparkline(list(self.memory_history), width=30),
            ""
        )
        
        return Panel(table, title="Memory Information", border_style="green")
    
    def _create_disk_panel(self):
        """Create disk information panel with I/O monitoring"""
        disks = self._get_disk_info()
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Device", style="cyan")
        table.add_column("Mount Point")
        table.add_column("File System")
        table.add_column("Used")
        table.add_column("Total")
        table.add_column("Usage")
        
        for disk in disks[:5]:  # Show top 5 disks
            # Color code based on usage
            usage_color = "green"
            if disk['percent'] > self.thresholds['disk_critical']:
                usage_color = "red"
            elif disk['percent'] > self.thresholds['disk_warning']:
                usage_color = "yellow"
            
            usage_bar = self._create_progress_bar(disk['percent'], width=15)
            table.add_row(
                disk['device'][:10],  # Truncate long device names
                disk['mountpoint'][:15],  # Truncate long mount points
                disk['fstype'],
                self._format_bytes(disk['used']),
                self._format_bytes(disk['total']),
                usage_bar
            )
        
        # Add disk I/O information
        current_io = self._get_disk_io_counters()
        if current_io != (0, 0) and self.prev_disk_counters != (0, 0):
            read_speed = (current_io[0] - self.prev_disk_counters[0]) / self.update_interval
            write_speed = (current_io[1] - self.prev_disk_counters[1]) / self.update_interval
            
            if read_speed > 0 or write_speed > 0:
                table.add_row(
                    "I/O Speed",
                    f"R: {self._format_bytes(read_speed)}/s",
                    f"W: {self._format_bytes(write_speed)}/s",
                    "", "", ""
                )
        
        self.prev_disk_counters = current_io
        
        return Panel(table, title="Disk Usage & I/O", border_style="yellow")
    
    def _create_network_panel(self):
        """Create network information panel with enhanced monitoring"""
        net_info = self._get_network_info()
        connections = self._get_network_connections()
        
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
        
        # Connection summary
        if connections:
            table.add_row(
                "Connections",
                f"Est: {connections.get('established', 0)}",
                f"Listen: {connections.get('listen', 0)}"
            )
        
        # Network history
        total_speed = net_info['download_speed'] + net_info['upload_speed']
        self.network_history.append(total_speed / 1024)  # Convert to KB/s
        table.add_row(
            "Activity",
            self._create_sparkline(list(self.network_history), width=30),
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
                gpu['name'][:20],  # Truncate long GPU names
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
        
        # Battery level with color coding
        battery_color = "green"
        if battery_info['percent'] < 20:
            battery_color = "red"
        elif battery_info['percent'] < 50:
            battery_color = "yellow"
        
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
        """Create top processes panel with enhanced information"""
        processes = self._get_top_processes(limit=15)
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("PID", justify="right", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("CPU%", justify="right")
        table.add_column("Mem%", justify="right")
        table.add_column("Memory", justify="right")
        
        for i, proc in enumerate(processes):
            memory_info = proc.get('memory_info')
            memory_mb = 0
            if memory_info and hasattr(memory_info, 'rss'):
                memory_mb = memory_info.rss / (1024 * 1024)
            elif isinstance(memory_info, dict) and 'rss' in memory_info:
                memory_mb = memory_info['rss'] / (1024 * 1024)
            
            # Highlight high resource usage
            cpu_style = "red" if proc['cpu_percent'] > 50 else "yellow" if proc['cpu_percent'] > 25 else "white"
            mem_style = "red" if proc['memory_percent'] > 10 else "yellow" if proc['memory_percent'] > 5 else "white"
            
            table.add_row(
                str(proc['pid']),
                proc['name'][:20],
                Text(f"{proc['cpu_percent']:.1f}", style=cpu_style),
                Text(f"{proc['memory_percent']:.1f}", style=mem_style),
                f"{memory_mb:.0f}MB"
            )
        
        # Add sort indicator
        sort_indicator = f"Sorted by: {self.process_sort_key.replace('_', ' ').title()}"
        
        return Panel(table, title=f"Top Processes - {sort_indicator}", border_style="white")
    
    def _create_docker_panel(self):
        """Create Docker containers panel"""
        docker_info = self._get_docker_info()
        
        if not docker_info:
            return Panel(
                Align.center("Docker not available or no containers"),
                title="Docker Containers",
                border_style="dim"
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Container", style="cyan")
        table.add_column("Image")
        table.add_column("Status")
        table.add_column("Ports")
        
        for container in docker_info[:10]:  # Show up to 10 containers
            status_color = "green" if container['status'] == 'running' else "red"
            ports_str = ", ".join([f"{k}:{v}" for k, v in container['ports'].items()]) if container['ports'] else "None"
            
            table.add_row(
                container['name'][:15],
                container['image'][:25],
                Text(container['status'], style=status_color),
                ports_str[:20]
            )
        
        return Panel(table, title="Docker Containers", border_style="blue")
    
    def _create_services_panel(self):
        """Create system services panel"""
        services = self._get_system_services()
        
        if not services:
            return Panel(
                Align.center("No services information available"),
                title="System Services",
                border_style="dim"
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Service", style="cyan")
        table.add_column("Status")
        table.add_column("Description")
        
        for service in services[:15]:  # Show up to 15 services
            status_color = "green" if service['status'] == 'active' else "yellow"
            
            table.add_row(
                service['name'][:20],
                Text(service['status'], style=status_color),
                service['description'][:40]
            )
        
        return Panel(table, title="System Services", border_style="green")
    
    def _create_alerts_panel(self):
        """Create alerts panel"""
        if not self.alerts:
            return Panel(
                Align.center("No recent alerts"),
                title="System Alerts",
                border_style="green"
            )
        
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Time", style="dim")
        table.add_column("Level")
        table.add_column("Message", style="cyan")
        
        for alert in self.alerts[-10:]:  # Show last 10 alerts
            level_color = "red" if alert['level'] == 'critical' else "yellow"
            time_str = alert['time'].strftime("%H:%M:%S")
            
            table.add_row(
                time_str,
                Text(alert['level'].upper(), style=level_color),
                alert['message'][:50]
            )
        
        border_color = "red" if any(a['level'] == 'critical' for a in self.alerts[-3:]) else "yellow"
        return Panel(table, title="System Alerts", border_style=border_color)
    
    def _create_help_panel(self):
        """Create help panel with keyboard shortcuts"""
        help_text = """
[bold cyan]Keyboard Shortcuts:[/bold cyan]

[yellow]q[/yellow] - Quit application
[yellow]h[/yellow] - Toggle this help
[yellow]1[/yellow] - Main dashboard view
[yellow]2[/yellow] - Docker containers view  
[yellow]3[/yellow] - System alerts view

[yellow]c[/yellow] - Sort processes by CPU
[yellow]m[/yellow] - Sort processes by Memory
[yellow]p[/yellow] - Sort processes by PID
[yellow]n[/yellow] - Sort processes by Name

[yellow]s[/yellow] - Toggle system info panel
[yellow]u[/yellow] - Toggle CPU panel
[yellow]r[/yellow] - Toggle memory panel
[yellow]d[/yellow] - Toggle disk panel
[yellow]t[/yellow] - Toggle network panel
[yellow]g[/yellow] - Toggle GPU panel
[yellow]b[/yellow] - Toggle battery panel

[yellow]+[/yellow] - Increase update interval
[yellow]-[/yellow] - Decrease update interval

[bold green]Current Configuration:[/bold green]
Update Interval: {self.update_interval:.1f}s
Process Sort: {self.process_sort_key.replace('_', ' ').title()}
        """
        
        return Panel(
            Align.center(help_text),
            title="Help & Controls",
            border_style="cyan"
        )

def main():
    """Main entry point"""
    try:
        monitor = SystemMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\nExiting system monitor...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting system monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
