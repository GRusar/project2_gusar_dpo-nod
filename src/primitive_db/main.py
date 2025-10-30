#!/usr/bin/env python3

from .engine import run, welcome


def main():
    print("DB project is running!")
    welcome()
    run()

if __name__ == "__main__":
    main()