"""
main.py
=======

Project Modesty

This is the only file that should ever be started manually.

Author:
    Andrew & ChatGPT
"""

from Runtime.Core.bootstrap import startup
from Runtime.study import run
from Runtime.Time import PresenceSession


def main():
    presence = PresenceSession().begin()
    try:
        startup(presence)
        run(presence)
    finally:
        presence.shutdown()


if __name__ == "__main__":
    main()
