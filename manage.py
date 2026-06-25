#!/usr/bin/env python
import os
import sys


# Стандартная точка входа для команд Django.
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowers_django.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
