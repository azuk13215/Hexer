import os
import time

from core.commands.directory_command import fileApp
from core.commands.sytems_commads import sysApp
from core.commands.time_commands import timeApp
from core.commands.help_command import helpApp, COMMAND_HELP_DICT
from core.commands.network_commands import netApp
from core.commands.setting_commands import settingApp
from core.commands.commands_for_w_memory import memoryApp

class Hexer:
    @staticmethod
    def handle_command(cmd: str, start_time=None):
        parts = cmd.strip().split()

        if not parts:
            return ("info", "", os.getcwd())

        command = parts[0].lower()
        args = parts[1:]

        # HELP FLAG
        if "--help" in args or "-h" in args:
            key = command.lower()

            if key in COMMAND_HELP_DICT:
                return (
                    "info",
                    f"{key}: {COMMAND_HELP_DICT[key]}",
                    os.getcwd()
                )

            return (
                "error",
                f"No help available for '{command}'",
                os.getcwd()
            )

        # COMMAND APPS
        apps = [
            fileApp,
            sysApp,
            timeApp,
            helpApp,
            netApp,
            settingApp,
            memoryApp
        ]

        for app in apps:
            result = app(cmd)

            if result is not None:
                return result

        return (
            "error",
            f"Unknown command: {command}",
            os.getcwd()
        )


    @staticmethod
    def run_terminal():
        start_time = time.time()

        while True:
            cmd = input(f"{os.getcwd()} -> ")

            tag, message, cwd = Hexer.handle_command(
                cmd,
                start_time
            )

            # Only the CLI prints
            print(message)

            if tag == "exit":
                break
    