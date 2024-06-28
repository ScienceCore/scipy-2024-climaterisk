# Generates .netrc file, prompting user for EarthData credentials
# Warning: overwrites existing .netrc file

from getpass import getpass
from pathlib import Path
import sys
NETRC_PATH = Path('~/.netrc').expanduser()
TEMPLATE = "machine urs.earthdata.nasa.gov login {USERNAME} password {PASSWORD}\n"

if NETRC_PATH.exists():
    print("Warning: .netrc exists already; back up to avoid losing credentials")
    sys.exit(1)

username = getpass(prompt="NASA EarthData login:    ")
password = getpass(prompt="NASA EarthData password: ")

NETRC_PATH.write_text(TEMPLATE.format(USERNAME=username, PASSWORD=password))
NETRC_PATH.chmod(0o600)
