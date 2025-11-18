import os
import time
import datetime
import getpass
from core.directory_command import fileApp
from core.sytems_commads import sysApp
from core.time_commands import timeApp
from core.help_command import helpApp
from core.network_commands import netApp

class Hexer:
    @staticmethod
    def handle_command(cmd: str, start_time=None):
        parts = cmd.strip().split()
        if not parts:
            return ("info", "", os.getcwd())

        command = parts[0].lower()
        args = parts[1:]
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
