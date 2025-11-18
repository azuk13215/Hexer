def helpApp(cmd: str):
    import os
    parts = cmd.strip().split()
    if not parts:
        return ("info", "", os.getcwd())

    command = parts[0].lower()

    if command != "help":
        return None

    list_help = """
        ===================== Hexer Help =====================

        help        - Show this help menu
        exit        - Exit the terminal
        time        - Show exact system time
        uptime      - Show system uptime
        mkdir       - Create a directory
        cd          - Change directory
        whoami      - Show username
        pwd         - Print working directory
        ls          - List directory contents
        touch       - Create an empty file
        echo        - Print text or write to file
        cat         - Show file contents
        rm          - Remove file/directory
        rename      - Rename file/directory
        cp          - Copy file
        mv          - Move (rename) file
        find        - Search for files
        grep        - Search text in files
        tree        - Show directory tree
        history     - Show command history
        sleep       - Pause for N seconds
        timer       - Start countdown timer
        ping        - Ping host
        ip          - Show IP information

        =======================================================
        """

    return ("info", list_help, os.getcwd())
