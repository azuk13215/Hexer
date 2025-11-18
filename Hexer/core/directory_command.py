import os
import time
import shutil
import shlex

def fileApp(cmd: str):
    parts = shlex.split(cmd.strip())
    if not parts:
        return ("info", "", os.getcwd())
    
    command = parts[0].lower()
    args = parts[1:]

    # --- mkdir command ---
    if command == "mkdir":
        if len(args) == 0:
            return ("error", "Specify the directory name", os.getcwd())
        folder_name = args[0]
        try:
            os.mkdir(folder_name)
            return ("success", f"Directory '{folder_name}' created", os.getcwd())
        
        except FileExistsError:
            return ("error", f"Directory '{folder_name}' already exists", os.getcwd())
        
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- cd command ---
    if command == "cd":
        path = args[0] if len(args) >= 1 else os.path.expanduser("~")
        try:
            os.chdir(os.path.expanduser(path))
            return ("success", f"Changed directory to: {os.getcwd()}", os.getcwd())
        
        except FileNotFoundError:
            return ("error", f"Directory '{path}' not found", os.getcwd())
        
        except NotADirectoryError:
            return ("error", f"'{path}' is not a directory", os.getcwd())
        
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    if command == "pwd":
        return ("info", f"Current directory: {os.getcwd()}", os.getcwd())
    
    # --- ls command ---
    if command == "ls":
        # Default: show only visible files
        show_all = "-a" in args

        try:
            items = os.listdir(os.getcwd())
            # If no -a flag, filter out files
            if not show_all:
                items = [i for i in items if not i.startswith(".")]

            if not items:
                return ("info", "(empty directory)", os.getcwd())
            
            # Join all items in one string separated by spaces
            output = " ".join(items)
            return ("info", output, os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
            
    if command == "touch":
        if len(args) == 0:
            return ("error", "Specify the filename", os.getcwd())
        
        file_name = args[0]
        try:
            if os.path.exists(file_name):
                return ("success", f"Update timesamp of '{file_name}'", os.getcwd())
            else:
                with open(file_name, 'a'):
                    pass
                return ("success", f"Created file '{file_name}'", os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())

    # --- echo command ---
    if command == "echo":
        # if nothing after 'echo', just return an empty line
        if not args:
            return ("info", "", os.getcwd())
        
        # Check if the user wants to redirect output to a file
        if '>' in args or '>>' in args:
            try:
                # Datermine redirection mode and the index of the operator
                if '>>' in args:
                    i = args.index('>>')
                    mode = 'a' # append mode
                else:
                    i = args.index('>')
                    mode = 'w' # write (overwrite) mode

                    # Everythings before > or >> is the text to write
                    text = " ".join(args[:i])

                    # Everythings after > or >> should contain the filename
                    if i + 1 >= len(args):
                        return ("error", "No filename specified", os.getcwd())
                    filename = args[i + 1]

                    # Write or append text to the file
                    with open(filename, mode, encoding="utf-8") as f:
                        f.write(text + "\n")

                    # Return a success message
                    action = "appended to" if mode == 'a' else "written to"

                    return ("success", f"Text {action} '{filename}'", os.getcwd())
            except Exception as e:
                # Handle any file-related errors
                return ("error", f"Error: {e}", os.getcwd())
        
        # If there is no redicretion, just return the text for display
        text = " ".join(args)
        return ("info", text, os.getcwd())
    
    # --- cat command ---
    if command == "cat":
        # Check if user specified at least one file
        if not args:
            return ("error", "Specify at least one filename", os.getcwd())
        
        output = []

        # Loop through all provided filenames
        for filename in args:
            try:
                # Expand ~ and relative paths
                path = os.path.expanduser(filename)

                # Read and collect file contents
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    output.append(f"--- {filename}---\n{content}")
            except FileNotFoundError:
                output.append(f"Error: File '{filename}' not found.")

            except PermissionError:
                output.append(f"Error: Permission denied for '{filename}'.")

            except IsADirectoryError:
                output.append(f"Error: '{filename}' is a directory.")
            
            except Exception as e:
                output.append(f"Error: {e}")

        # Combine all results into one string 
        return ("info", "\n\n".join(output), os.getcwd())

    # --- rm command ---
    if command == "rm":
        # Check if user gave at least one argument
        if not args:
            return ("error", "Specify the file or directory to remove", os.getcwd())
        
        target = os.path.expanduser(args[0])

        # Optional flag -r for recurcive folder deletion
        recursive = "-r" in args or "-rf" in args

        try:
            if os.path.isdir(target):
                if recursive:
                    # Remove folder and all its contents
                    shutil.rmtree(target)
                    return ("success", f"Directory '{target}' removed recursively", os.getcwd())
                else:
                    # Warn user if they try to remove a directory without -r
                    return ("error", f"'{target}' is a directory. Use 'rm -r {target}'", os.getcwd())
            elif os.path.isfile(target):
                os.remove(target)
                return ("success", f"File '{target}' not found", os.getcwd())
        except PermissionError:
            return ("error", f"Permission denied for '{target}'", os.getcwd())
        
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- rename command ---
    if command == "rename":
        # Expected format: rename old.txt < new.txt
        if len(args) < 3 or args[1] != "<":
            return ("error", "Usage: rename <old_name> < <new_name>", os.getcwd())
        
        old_name = os.path.expanduser(args[0])
        new_name = os.path.expanduser(args[2])

        if not os.path.exists(old_name):
            return ("error", f"File '{old_name}' not found", os.getcwd())
        try:
            os.rename(old_name, new_name)
            return ("success", f"Renamedv '{old_name}' -> '{new_name}'", os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- cp command ---
    if command == "cp":
        if len(args) < 2:
            return ("error", "Usage: cp <source> <destination>", os.getcwd())
        
        source = os.path.expanduser(args[0])
        destination = os.path.expanduser(args[1])

        recursive = "-r" in args

        try:
            if os.path.isdir(source):
                if recursive:
                    if os.path.exists(destination):
                        return ("error", f"Destination '{destination}' already exists", os.getcwd())
                    shutil.copytree(source, destination)
                    return ("success", f"Directory '{source}' copied recursively to '{destination}'", os.getcwd())
                else:
                    return ("error", "cp: omitting directory (use -r to copy directories)", os.getcwd())
            else:
                shutil.copy2(source, destination)
                return ("success", f"File '{source}' copied to '{destination}'", os.getcwd())
        except FileNotFoundError:
            return ("error", f"Source '{source}' not found", os.getcwd())
        
        except PermissionError:
            return ("error", f"Permission denied", os.getcwd())
        
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- mv command ---
    if command == "mv":
        # Usage: mv <source> <destitation>
        if len(args) < 2:
            return ("error", "Usage: mv <source> <destination>", os.getcwd())
        source = os.path.expanduser(args[0])
        destination = os.path.expanduser(args[1])

        try:
            if not os.path.exists(source):
                return ("error", f"Source '{source}' not found", os.getcwd())
            
            # If destination is a directory, move file *into* that directory
            if os.path.isdir(destination):
                dest_path = os.path.join(destination, os.path.basename(source))
            else:
                dest_path = destination
                shutil.move(source, dest_path)
                return ("success", f"Moved '{source}' -> '{dest_path}'", os.getcwd())
        except PermissionError:
            return ("error", "Permission denied", os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- head command ---
    if command == "head":
        if not args:
            return ("error", "Usage: head <filename> [-n <number_of_lines>]", os.getcwd())
        filename = os.path.expanduser(args[0])

        # Defult number of lines to show
        num_lines = 10

        # Check for optional -n flag
        if "-n" in args:
            try:
                n_index = args.index("-n")
                num_lines = int(args[n_index + 1])
            except (IndexError, ValueError):
                return ("error", "Invalid of missing value for -n", os.getcwd())
        
        if not os.path.exists(filename):
            return ("error", f"File '{filename}' is a directory", os.getcwd())
        
        if os.path.isdir(filename):
            return ("error", f"'{filename}' is a directory", os.getcwd())
        
        try:
            with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                # Read the first N lines
                lines = []
                for i in range(num_lines):
                    line = f.readline()
                    if not line:
                        break
                lines.append(line.rstrip("\n"))
                content = "\n".join(lines)
                return ("info", content if content else "(file is empty)", os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    # --- find command ---
    if command == "find":
        # Usage: find <name> [-r]
        if not args:
            return ("error", "Usage: find <name or part> [-r]", os.getcwd())
    
        # What we are looking for
        search_name = args[0].lower()
        recursive = "-r" in args

        start_dir = os.getcwd()
        matches = []

        try:
            if recursive:
                # Walk through all subdirectories
                for root, dirs, files in os.walk(start_dir):
                    for name in dirs + files:
                        if search_name in name.lower():
                            full_path = os.path.join(root, name)
                            matches.append(full_path)
            else:
                # Search only in current directory
                for name in os.listdir(start_dir):
                    if search_name in name.lower():
                        matches.append(os.path.join(start_dir, name))

            # Output result
            if matches:
                result = "\n".join(matches)
                return ("info", result, os.getcwd())
            else:
                return ("info", f"No matches for '{search_name}'", os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    if command == "grep":
        if len(args) < 2:
            return ("error", "Usage: grep <pattern> <file>")
        
        pattern = args[0]
        file_path = args[1]

        if not os.path.exists(file_path):
            return ("error", f"File '{file_path}' not found")
        
        try:
            matched_lines = []

            with open(file_path, "r", encoding="utf-8") as f:
                for lines in f:
                    if pattern in line:
                        matched_lines.append(line.rstrip())

                if matched_lines:
                    result_text = "\n".join(matched_lines)
                    return ("success", result_text, os.getcwd())
                else:
                    return ("success", "No matces found", os.getcwd())
                
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    if command == "open":
        if len(args) == 0:
            return ("error", "Usage: open <file> [--flags]", os.getcwd())
        # -------------------------
        # Perse arguments
        # -------------------------
        file_path = None
        flag = None
        value = None
        edit_text = None

        for arg in args:
            if arg.startswith("--"):
                flag = arg
            elif flag == "--edit":
                edit_text = arg
            elif flag in ("--tail", "--head"):
                try:
                    value = int(arg)
                except:
                    return ("error", f"Invalid number for {flag}")
            elif flag == "--lines":
                value = arg # example: "3-10"
            else:
                file_path = arg

        if not file_path:
            return ("error", "Specify file to open", os.getcwd())

        full_path = os.path.abspath(file_path)
        if not os.path.exists(full_path):
            return ("error", f"File '{file_path}' not found", os.getcwd())

        if os.path.isdir(full_path):
            return ("error", f"'{file_path}' is a directory, not a file", os.getcwd())

        # -------------------------
        # --edit
        # -------------------------
        if flag == "--edit":
            if edit_text is None:
                return ("error", "Usage: open <file> --edit \"new content\"", os.getcwd())

            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(edit_text)
                return ("success", f"File '{file_path}' updated", os.getcwd())
            except Exception as e:
                return ("error", f"Error: {e}", os.getcwd())

        # -------------------------
        # Read file
        # -------------------------
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
        # -------------------------
        # --binary flag (HEX dump)
        # -------------------------
        if flag == "--binary":
            try:
                with open(full_path, "rb") as f:
                    data = f.read()
                hex_dump = " ".join(f"{b:02x}" for b in data)
                return ("info", hex_dump, os.getcwd())
            except Exception as e:
                return ("error", f"Error: {e}", os.getcwd())
        
        # -------------------------
        # --lines flag (line range)
        # -------------------------
        if flag == "--lines":
            if value is None or "-" not in value:
                return ("error", "Usage: open <file> --lines 5-10", os.getcwd())
            
            try:
                start, end = value.split("-")
                start = int(start)
                end = int(end)
                selected = "".join(lines[start:end])
                return ("info", selected, os.getcwd())
            except:
                return ("error", "Invalid line range", os.getcwd())
            
        # -------------------------
        # --tail flag
        # -------------------------
        if flag == "--tail":
            if value is None:
                return ("error", "Usage: open <file> --tail 20", os.getcwd())
            
            selected = "".join(lines[-value:])
            return ("info", selected, os.getcwd())
        
        # -------------------------
        # --head flag
        # -------------------------
        if flag == "--head":
            if value is None:
                return ("error", "Usage: open <file> --head 20", os.getcwd())
            
            selected = "".join(lines[:value])
            return ("info", selected, os.getcwd())
        
        # -------------------------
        # Defult: read full file
        # -------------------------
        return ("info", "".join(lines), os.getcwd())

    return None
