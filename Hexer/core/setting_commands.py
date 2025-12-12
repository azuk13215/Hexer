import shlex
import os
import subprocess
import json

def settingApp(cmd: str):
    parts = shlex.split(cmd.strip())
    if not parts:
        return ("info", "", os.getcwd())
    
    command = parts[0].lower()
    args = parts[1:]

    WAL_FILE = os.path.expanduser("/home/andriy/Hexer/Hexer/data/wallpaper_history.json")
    LANG_FILE = os.path.expanduser("/home/andriy/Hexer/Hexer/data/last_lang.json")

    def check_help(command, args):
        from core.help_command import COMMAND_HELP_DICT
        if "--help" in args or "-h" in args:
            if command in COMMAND_HELP_DICT:
                return ("info", f"Help for '{command}': \n{COMMAND_HELP_DICT[command]}", os.getcwd())
            else:
                return ("error", f"No help available for '{command}'")
            
    def load_lang():
        if not os.path.exists(LANG_FILE):
            return {}
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def save_lang(data: dict):
        try:
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    def bt_run(cmd):
        try:
            output = subprocess.check_output(
                ["bluetoothctl"] + cmd,
                stderr=subprocess.STDOUT,
                text=True
            )
            return output.strip()
        except Exception as e:
            return f"Error: {e}"
    
    if command == "wallpaper":
        # ----------- load -----------
        def load_last_wallpaper():
            if not os.path.exists(WAL_FILE):
                return {"last_wallpaper": None}
            try:
                with open(WAL_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"last_wallpaper": None}
        
        # ----------- save -----------
        def save_last_wallpaper(path: str):
            with open(WAL_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_wallpaper": path}, f, indent=4)
        history = load_last_wallpaper()

        def detect_dekstop_env():
            # standard environment variable
            de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            session = os.environ.get("DESKTOP_SESSION", "").lower()
            
            # Basic DE
            if "gnome" in de:
                return "gnome"
            if "kde" in de or "plasma" in de:
                return "kde"
            if "xfce" in de:
                return "xfce"
            if "lxqt" in de:
                return "lxqt"
            if "cinnamon" in de:
                return "cinnamon"
            if "mate" in de:
                return "mate"
            
            # Tiling WMs
            if "i3" in session:
                return "i3"
            if "hyprland" in session:
                return "hyprland"
            if "sway" in session:
                return "sway"

            # if didn't recognize it
            return "unknown"

        # === flags ===
        if "--history" in args:
            return ("info", f"Last wallpaper: {history['last_wallpaper']}", os.getcwd())

        if "--get" in args:
            return ("info", history["last_wallpaper"], os.getcwd())

        # === no args given ===
        if len(args) == 0:
            return ("error", "Usage: wallpaper <image_path> or --history", os.getcwd())

        # === resolve path (supporting ~) ===
        image_path = os.path.expanduser(args[0])
        image_path = os.path.abspath(image_path)

        if not os.path.exists(image_path):
            return ("error", f"File not found: {image_path}", os.getcwd())

        # === detect desktop environment ===
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

        try:
            if "gnome" in desktop:
                cmd = [
                    "gsettings", "set",
                    "org.gnome.desktop.background", "picture-uri",
                    f"file://{image_path}"
                ]
                subprocess.run(cmd, check=True)
                save_last_wallpaper(image_path)
                return ("success", f"Wallpaper set (GNOME): {image_path}", os.getcwd())

            elif "kde" in desktop or "plasma" in desktop:
                # KDE uses a DBus call
                script = f"""
                var allDesktops = desktops();
                for (i=0;i<allDesktops.length;i++) {{
                    d = allDesktops[i];
                    d.wallpaperPlugin = "org.kde.image";
                    d.currentConfigGroup = Array("Wallpaper","org.kde.image","General");
                    d.writeConfig("Image", "file://{image_path}")
                }}
                """
                subprocess.run(["qdbus-qt5", "org.kde.plasmashell", "/PlasmaShell",
                                "org.kde.PlasmaShell.evaluateScript", script], check=True)
                save_last_wallpaper(image_path)
                return ("success", f"Wallpaper set (KDE Plasma): {image_path}", os.getcwd())

            elif "xfce" in desktop:
                subprocess.run([
                    "xfconf-query", "--channel", "xfce4-desktop",
                    "--property", "/backdrop/screen0/monitor0/image-path",
                    "--set", image_path
                ], check=True)
                save_last_wallpaper(image_path)
                return ("success", f"Wallpaper set (XFCE): {image_path}", os.getcwd())

            else:
                return ("error", f"Unsupported environment: {desktop}", os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    if command == "volumeinfo":
        try:
            result = subprocess.run(
                ["pactl",
                 "get-sink-volume", "@DEFULT_SINK@"],
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 text=True
            )

            if result.returncode != 0:
                return ("error", "Error: pactl is not avaible on your system", os.getcwd())
            
            output = result.stdout.strip()

            mute_result = subprocess.run(
                ["pactl", 
                 "get-sink-mute", "@DEFULT_SINK@"],
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 text=True
            )

            mute_outout = mute_result.stdout.strip()

            # example: "Volume: front-left: 65536 / 100% / 0.00 dB"

            import re
            match = re.search(r"(\d+)%", output)

            volume_percent = match.group(1) if match else "Unknown"
            is_muted = "yes" in mute_outout.lower()

            info = [
                f"Volume: {volume_percent}%",
                f"Mute: {'ON' if is_muted else 'OFF'}"
            ]

            return ("info", "\n".join(info), os.getcwd())
        
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    if command == "lang":
        # loading JSON from settings
        lang_settings = load_lang()

        # --- SET LANGUAGE ---
        if len(args) >= 2 and args[0] == "-s":
            new_lang = args[1]

            lang_settings["last_lang"] = new_lang
            save_lang(lang_settings)

            return ("success", f"Saved language: {new_lang}", os.getcwd())

        # --- SHOW CURRENT SYSTEM LANGUAGE ---
        system_lang = os.environ.get("LANG", "unknown")

        # en_US.UTF-8 -> en
        short = system_lang.split(".")[0].split("_")[0]

        last_saved = lang_settings.get("last_lang", "none")

        message = (
            f"System language: {short} ({system_lang})\n"
            f"Last saved language: {last_saved}"
        )

        return ("info", message, os.getcwd())
    