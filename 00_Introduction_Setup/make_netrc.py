# This script generates .netrc file, prompting user for EarthData credentials.
# Delete or rename ~/.netrc before executing this script (it won't overwrite a
# pre-existing ~/.netrc file).

from getpass import getpass
from pathlib import Path
import sys

NETRC_PATH = Path('~/.netrc').expanduser()
TEMPLATE = " ".join(["machine", "urs.earthdata.nasa.gov", "login",
                     "{USERNAME}", "password", "{PASSWORD}\n"])

if NETRC_PATH.exists():
    print("Warning: ~/.netrc exists already (this script won't overwrite).")
    print("         Delete ~/.netrc first or back up to avoid losing credentials.")
    sys.exit(1)

username = input("NASA EarthData login:    ")
password = getpass(prompt="NASA EarthData password: ")

NETRC_PATH.write_text(TEMPLATE.format(USERNAME=username, PASSWORD=password))
NETRC_PATH.chmod(0o600)
