import time
import os
import datetime

def timeApp(cmd: str, start_time=None):

    parts = cmd.strip().split()
    if not parts:
        return ("info", "", os.getcwd())

    command = parts[0].lower()
    args = parts[1:]

    def check_help(command, args):
        from core.help_command import COMMAND_HELP_DICT
        if "--help" in args or "-h" in args:
            if command in COMMAND_HELP_DICT:
                return ("info", f"Help for '{command}': \n{COMMAND_HELP_DICT[command]}", os.getcwd())
            else:
                return ("error", f"No help available for '{command}'")

    # --- sleep ---
    if command == "sleep":
        import time

        if len(args) == 0:
            return ("error", "Usage: sleep <seconds> or sleep -m <milliseconds>", os.getcwd())

        try:
            # sleep -m 150  (150 ms)
            if args[0] in ("-m", "--ms"):
                if len(args) < 2:
                    return ("error", "Usage: sleep -m <milliseconds>", os.getcwd())
                ms = float(args[1])
                time.sleep(ms / 1000.0)
                return ("success", f"Slept for {ms} ms", os.getcwd())

            # sleep 2.5  (seconds)
            seconds = float(args[0])
            time.sleep(seconds)
            return ("success", f"Slept for {seconds} seconds", os.getcwd())

        except ValueError:
            return ("error", "Time must be a number", os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    # --- timer ---
    if command == "timer":
        import time

        if len(args) == 0:
            return ("error", "Usage: timer <seconds> [-msg <text>] or timer -m <milliseconds> [-msg <text>]", os.getcwd())

        milliseconds_mode = False
        message = "Time is up!"
        time_value = None

        # Parse args
        i = 0
        while i < len(args):
            if args[i] in ("-m", "--ms"):
                milliseconds_mode = True
                try:
                    time_value = float(args[i + 1])
                except:
                    return ("error", "Invalid milliseconds value", os.getcwd())
                i += 2
            elif args[i] == "-msg":
                try:
                    message = args[i + 1]
                except:
                    return ("error", "No message provided", os.getcwd())
                i += 2
            else:
                # seconds mode (default)
                if time_value is None:
                    try:
                        time_value = float(args[i])
                    except:
                        return ("error", "Invalid time value", os.getcwd())
                i += 1

        if time_value is None:
            return ("error", "Time is not specified", os.getcwd())

        # sleep
        if milliseconds_mode:
            time.sleep(time_value / 1000.0)
            return ("info", f"[TIMER] {message} (after {time_value} ms)", os.getcwd())
        else:
            time.sleep(time_value)
            return ("info", f"[TIMER] {message} (after {time_value} seconds)", os.getcwd())
    
    if command == "time":
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return ("info", f"Current time: {now}", os.getcwd())
    
    if command == "uptime":
        if not start_time:
            return ("error", "Uptime tracking not started", os.getcwd())
        uptime = time.time() - start_time
        h, rem = divmod(int(uptime), 3600)
        m, s = divmod(rem, 60)
        return ("info", f"Uptime: {h:02d}:{m:02d}:{s:02d}", os.getcwd())
    
    if command == "exit":
        import time

        if not args:
            return ("exit", "Exiting...", os.getcwd())
        
        flag = args[0]
        if flag == "-t":
            if len(args) < 2:
                return ("error", "after '-t' you need to specify the number of seconds", os.getcwd())
            
            try:
                delay = int(args[1])
            except ValueError:
                return ("error", "time must be a number", os.getcwd())
        
        if flag == "-tm":
            if len(args) < 2:
                return ("error", "after '-tm' you need to specify the number of milliseconds", os.getcwd())
            try:
                delay = int(args[1]) / 1000.0
            except ValueError:
                return ("error", "time must be a number", os.getcwd())
            
            time.sleep(delay)
            return ("exit", "Exiting...", os.getcwd())
        
    return None
