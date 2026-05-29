import os
import zipfile

def memoryApp(cmd: str):
    parts = cmd.strip().split()
    if not parts:
        return ("info", "", os.getcwd())

    command = parts[0].lower()
    args = parts[1:]

    if command == "size":
        if not args:
            return ("error", "Usage: size <file_path>", os.getcwd())

        file_path = args[0]

        try:
            size_in_bytes = os.path.getsize(file_path)
            return ("info", f"size file '{file_path}': {size_in_bytes} bytes", os.getcwd())

        except FileNotFoundError:
            return ("error", f"file '{file_path}' is not found", os.getcwd())

        except OSError as e:
            return ("error", f"Error getting file size: {e}", os.getcwd())
        
    if command == "compress":
        if not args:
            return ("error", "Usage compress <file_path>", os.getcwd())
        
        file_path = args[0]
        zip_name = args[1]

        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, file_path)
                    zf.write(full_path, arcname)
            
        return ("success", "successfully compress", os.getcwd())
        
    return None