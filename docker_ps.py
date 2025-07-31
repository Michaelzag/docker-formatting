#!/usr/bin/env python3

import subprocess
import json
import sys
import re
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from rich.text import Text

def get_docker_containers(show_all=False):
    """Get container information from docker"""
    cmd = ["docker", "ps", "--format", "json"]
    if show_all:
        cmd.insert(2, "-a")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error running docker command: {e}")
        return []

def extract_external_ports(ports_str):
    """Extract external port numbers from port string"""
    if not ports_str:
        return ""
    matches = re.findall(r'0\.0\.0\.0:(\d+)', ports_str)
    return ",".join(matches) if matches else ""

def get_working_dir(labels):
    """Extract working directory from labels"""
    if not labels:
        return ""
    match = re.search(r'com\.docker\.compose\.project\.working_dir=([^,]+)', labels)
    return match.group(1) if match else ""

def get_container_uptime(container_id):
    """Get precise container uptime from docker inspect"""
    try:
        cmd = ["docker", "inspect", container_id, "--format", "{{.State.StartedAt}}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        started_at_str = result.stdout.strip()
        
        # Parse the timestamp
        started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        # Calculate uptime in seconds
        uptime_seconds = int((now - started_at).total_seconds())
        
        # Convert to appropriate unit with consistent formatting
        if uptime_seconds < 60:
            return f"{uptime_seconds:2d} s"
        elif uptime_seconds < 3600:
            minutes = uptime_seconds // 60
            return f"{minutes:2d} m"
        elif uptime_seconds < 86400:
            hours = uptime_seconds // 3600
            return f"{hours:2d} h"
        elif uptime_seconds < 2592000:  # 30 days
            days = uptime_seconds // 86400
            return f"{days:2d} d"
        elif uptime_seconds < 31536000:  # 365 days
            months = uptime_seconds // 2592000
            return f"{months:2d} mo"
        else:
            years = uptime_seconds // 31536000
            return f"{years:2d} y"
            
    except Exception:
        # Fallback to parsing the status string - need to get status from somewhere
        return "   ?"

def parse_status_for_time(status):
    """Fallback: parse time from status string"""
    # Extract time patterns from status with consistent formatting
    if "second" in status:
        match = re.search(r'(\d+)\s+second', status)
        if match:
            return f"{int(match.group(1)):2d} s"
    elif "minute" in status:
        match = re.search(r'(\d+)\s+minute', status)
        if match:
            return f"{int(match.group(1)):2d} m"
    elif "hour" in status:
        match = re.search(r'(\d+)\s+hour', status)
        if match:
            return f"{int(match.group(1)):2d} h"
    elif "day" in status:
        match = re.search(r'(\d+)\s+day', status)
        if match:
            return f"{int(match.group(1)):2d} d"
    
    return "   ?"

def get_status_style(status):
    """Return styling with better contrast"""
    if status == "healthy":
        return "bright_green"  # Brighter green for better visibility
    elif status == "unhealthy":
        return "bright_red" 
    elif status == "running":
        return "bright_cyan"  # Cyan instead of gray for better contrast
    elif status in ["stopped", "error"]:
        return "bright_red"
    elif status in ["starting", "restarting"]:
        return "bright_yellow"
    else:
        return "white"

def style_container_name(name, status):
    """Style container name based on status for subtle indication"""
    style = get_status_style(status)
    return Text(name, style=style)

def style_status_text(status):
    """Style the status text itself"""
    style = get_status_style(status)
    return Text(status, style=style)

def get_simple_status(status):
    """Simplify status to just the key state"""
    status_lower = status.lower()
    
    if "healthy" in status_lower:
        return "healthy"
    elif "unhealthy" in status_lower:
        return "unhealthy"
    elif "starting" in status_lower:
        return "starting"
    elif "up" in status_lower:
        return "running"
    elif "exited (0)" in status_lower:
        return "stopped"
    elif "exited" in status_lower:
        return "error"
    elif "dead" in status_lower:
        return "dead"
    elif "paused" in status_lower:
        return "paused"
    elif "restarting" in status_lower:
        return "restarting"
    else:
        return "unknown"

def extract_group_from_path(path):
    """Extract group for sorting purposes"""
    if not path:
        return "zzz_other"
    
    if "/actions-runner/" in path:
        return "a_github"
    elif path.startswith("/opt/"):
        return "b_opt"
    elif path.startswith("/var/"):
        return "c_var"
    else:
        return "d_other"

def main():
    # Always show all containers (running and stopped)
    containers = get_docker_containers(show_all=True)
    if not containers:
        print("No containers found")
        return
    
    # Process all containers
    container_data = []
    
    for container in containers:
        workdir = get_working_dir(container.get("Labels", ""))
        group = extract_group_from_path(workdir)
        uptime = get_container_uptime(container["ID"])
        simple_status = get_simple_status(container["Status"])
        
        container_data.append({
            "group": group,
            "id": container["ID"][:8],
            "name": container["Names"],
            "workdir": workdir or "-",
            "ports": extract_external_ports(container.get("Ports", "")),
            "uptime": uptime,
            "status": simple_status
        })
    
    # Sort by workdir first, then by name within same workdir
    container_data.sort(key=lambda x: (x["workdir"], x["name"]))
    
    console = Console()
    
    # Create table with better contrast styling
    table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
    table.add_column("ID", width=8, style="bright_black")  # Lighter gray for better contrast
    table.add_column("NAME", min_width=25, max_width=30)
    table.add_column("WORKDIR", min_width=30, max_width=50, style="white")  # Normal white instead of dim
    table.add_column("PORTS", width=10, style="cyan")  # Cyan instead of bright_blue for better contrast
    table.add_column("UPTIME", width=8, style="white")  # White instead of gray for readability
    table.add_column("STATUS", width=10)
    
    # Add all containers to the table with status-based styling
    for container in container_data:
        table.add_row(
            container["id"],
            style_container_name(container["name"], container["status"]),
            container["workdir"],
            container["ports"] or "-",
            container["uptime"],
            style_status_text(container["status"])
        )
    
    console.print(table)

if __name__ == "__main__":
    main()