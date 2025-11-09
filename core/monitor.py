import subprocess

def get_default_monitor():
    """Auto-detect PulseAudio monitor source."""
    try:
        sink = subprocess.check_output(["pactl", "get-default-sink"], text=True).strip()
        if sink:
            return sink + ".monitor"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        sources = subprocess.check_output(["pactl", "list", "short", "sources"], text=True)
        for line in sources.splitlines():
            if ".monitor" in line:
                return line.split()[1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    raise RuntimeError("No monitor")