import os
import json

from PyQt6.QtCore import Qt


class BindsManager:
    """Manage hotkeys and navigate through command history.

    Contains logic for handling up/down arrows and Enter in an input field.
    State and logic moved from HistoryLineEdit (core/gui.py).
    """

    HISTORY_FILE = os.path.expanduser(
        "/home/andriy/Hexer/Hexer/data/hexer_history.json"
    )

    def __init__(self, widget):
        self.widget = widget

        # List of command history: from the oldest to the newest.
        # We take the same data that is written to JSON (format: list {id, command}).
        self._history = self._load_history()

        # Index of the current position. len(_history) — "new" position (empty field),
        # from which the user starts browsing the history.
        self._history_index = len(self._history)

        # Draft: text that the user has started typing before browsing the history.
        self._draft = ""

    def _load_history(self):
        """Loads the history from the same JSON file that the rest of the code uses."""
        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Data is a list of {id, command} objects; we extract only commands.
            commands = []
            for item in data:
                cmd = item.get("command") if isinstance(item, dict) else item
                if cmd:
                    commands.append(str(cmd))
            return commands
        except (OSError, ValueError):
            return []

    def _apply_text(self, text):
        """Inserts the command into the widget's input line (cursor at the end)."""
        self.widget.set_input_text(text)

    def keyPressEvent(self, event):
        """Handles the hotkey.

        Returns True if the key is processed and should not be passed further,
        otherwise False - so that the widget processes it in the standard way (for example, Enter).
        """
        key = event.key()

        if key == Qt.Key.Key_Up:
            self._navigate_older()
            return True
        if key == Qt.Key.Key_Down:
            self._navigate_newer()
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # The command has been executed - we reset the navigation to its initial state.
            self._reset_navigation()

        return False

    def _navigate_older(self):
        """Arrow up: previous (older) command from the history."""
        if not self._history:
            return

        if self._history_index == len(self._history):
            # Only starting to browse — remember the current draft.
            self._draft = self.widget.get_input_text()
            self._history_index -= 1
        elif self._history_index > 0:
            self._history_index -= 1
        else:
            return  # already on the oldest command

        self._apply_text(self._history[self._history_index])

    def _navigate_newer(self):
        """Arrow down: more recent command; at the end — draft / empty field."""
        if self._history_index == len(self._history):
            return  # already at the end, nowhere to go

        self._history_index += 1

        if self._history_index == len(self._history):
            # Reached the end of the history — restore the draft.
            draft, self._draft = self._draft, ""
            self._apply_text(draft)
        else:
            self._apply_text(self._history[self._history_index])

    def _reset_navigation(self):
        """Returns navigation to its initial state after executing the command."""
        # Pereread the history, so that it includes only the recently entered commands.
        self._history = self._load_history()

        self._history_index = len(self._history)
        self._draft = ""
