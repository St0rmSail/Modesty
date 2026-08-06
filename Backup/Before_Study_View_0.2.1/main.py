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

def main():
    startup()


if __name__ == "__main__":
    startup()
    run()