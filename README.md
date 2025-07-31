# Docker Formatting

A Python utility that displays Docker container information in a beautifully formatted, color-coded table.

## Features

- **Comprehensive container view**: Shows all containers (running and stopped)
- **Color-coded status**: Visual indicators for container health and state
- **Smart grouping**: Organizes containers by their working directory paths
- **Precise uptime tracking**: Displays container runtime in human-readable format
- **Port extraction**: Shows only external ports for quick reference
- **Rich formatting**: Clean, readable table output with proper alignment

## Installation

Requires Python 3.8 or higher.

```bash
# Clone the repository
git clone <repository-url>
cd docker-formatting

# Install dependencies using uv (recommended)
uv pip install .

# Or install directly with pip
pip install rich
```

## Usage

Simply run the script:

```bash
python docker_ps.py
```

Or make it executable and run directly:

```bash
chmod +x docker_ps.py
./docker_ps.py
```

## Output

The utility displays a formatted table with the following columns:

- **ID**: Container ID (first 8 characters)
- **NAME**: Container name with color coding based on status
- **WORKDIR**: Docker Compose working directory
- **PORTS**: External ports mapped to the host
- **UPTIME**: Container runtime (seconds, minutes, hours, days, months, or years)
- **STATUS**: Container state (healthy, unhealthy, running, stopped, error, etc.)

### Status Color Coding

- =â **Bright Green**: Healthy containers
- =4 **Bright Red**: Unhealthy, stopped, or error states
- =5 **Bright Cyan**: Running containers
- =á **Bright Yellow**: Starting or restarting containers
- ª **White**: Unknown or other states

## Container Grouping

Containers are automatically grouped and sorted by their working directory:

1. GitHub Actions runners (`/actions-runner/`)
2. System services (`/opt/`)
3. Variable data services (`/var/`)
4. Other containers

## Requirements

- Docker installed and running
- Python 3.8+
- Rich library for terminal formatting

## License

[Specify your license here]