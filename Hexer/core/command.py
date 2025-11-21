import os
import time
from core.directory_command import fileApp
from core.sytems_commads import sysApp
from core.time_commands import timeApp
from core.help_command import helpApp, COMMAND_HELP_DICT
from core.network_commands import netApp

class Hexer:
    @staticmethod
    def handle_command(cmd: str, start_time=None):
        parts = cmd.strip().split()
        if not parts:
            return ("info", "", os.getcwd())
        
        command = parts[0].lower()
        args = parts[1:]

        # --- GLOBAL HELP FLAG HANLER ---

        # If user wrote: <command> --help OR -h
        if "--help" in args or "-h" in args:

            # lowercase command key
            key = command.lower()
            if key in COMMAND_HELP_DICT:
                return ("info", f"{key}: {COMMAND_HELP_DICT[key]}", os.getcwd())
            else:
                return ("error", f"No help available for '{command}'", os.getcwd())

        result_file = fileApp(cmd)
        if result_file is not None:
            return result_file
        
        result_sys = sysApp(cmd)
        if result_sys is not None:
            return result_sys
        
        result_time = timeApp(cmd)
        if result_time is not None:
            return result_time
        
        result_help = helpApp(cmd)
        if result_help is not None:
            return result_help
        
        result_net = netApp(cmd)
        if result_net is not None:
            return result_net

        parts = cmd.strip().split()
        if not parts:
            return ("info", "", os.getcwd())

        command = parts[0].lower()
        args = parts[1:]

    def run():
        start_time = time.time()
        while True:
            cmd = input(f"{os.getcwd()} -> ")
            tag, message, cwd = Hexer.handle_command(cmd, start_time)
            print(message)
            if tag == "exit":
                break
