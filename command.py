#!/usr/bin/python3
from src import TkCommander

if __name__ == "__main__":
    commander = TkCommander(timeout=None)
    commander.title("Camera commander")
    commander.command()
