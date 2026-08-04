import sys
from core.command import Hexer
from binds.binds import BindsManager
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
)

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import (
    QFont,
    QIcon,
    QColor,
    QTextCursor,
    QTextCharFormat,
    QShortcut,
    QKeySequence,
)

# --- minimalist palette (in the spirit of fish) ---
BG = "#1e1e1e"          # uniform window background (slightly gray, not black)
FG = "#d4d4d4"          # muted white text
DIM = "#8b8b8b"         # muted gray (path, cursor block)
ACCENT = "#c792ea"      # muted purple-pink (symbol of invitation)
TITLE_FG = "#e0e0e0"    # title bar text
ERR = "#e06c75"         # muted red for error messages
MONO = "Consolas"


class TitleBar(QWidget):
    """Slim custom title bar: title in the center, fullscreen buttons
    mode and closing on the right.

    Without standard OS elements (frameless window) and without dividing lines.
    The window can be dragged by the title bar with the mouse.
    """

    HEIGHT = 28
    SIDE = 44  # width of the button (there are two on the right — we balance them on the left with a doubled width)

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left "counterweight" space — to make the title strictly centered.
        layout.addSpacing(self.SIDE * 2)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"background: transparent; color: {TITLE_FG}; font-size: 12px;"
        )
        layout.addWidget(title_label, 1)

        fs_btn = QPushButton("▢")
        fs_btn.setFixedWidth(self.SIDE)
        fs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fs_btn.setStyleSheet(self._btn_style())
        fs_btn.setToolTip("Fullscreen (F11)")
        fs_btn.clicked.connect(self._toggle_fullscreen)
        self._fs_btn = fs_btn
        layout.addWidget(fs_btn)

        close_btn = QPushButton("×")
        close_btn.setFixedWidth(self.SIDE)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(self._btn_style())
        close_btn.clicked.connect(self._close_window)
        layout.addWidget(close_btn)

        self.setStyleSheet(f"background-color: {BG};")

    @staticmethod
    def _btn_style():
        return (
            "QPushButton {"
            f"  background: transparent; color: {DIM}; border: none;"
            "  font-size: 16px;"
            "}"
            "QPushButton:hover {"
            "  background: #2a2a2a; color: #ffffff;"
            "}"
        )

    def _close_window(self):
        self.window().close()

    def _toggle_fullscreen(self):
        self.window().toggle_fullscreen()

    def set_fullscreen_state(self, is_full):
        """Updates the button icon: ▣ — exit from fullscreen, ▢ — enter fullscreen."""
        self._fs_btn.setText("▣" if is_full else "▢")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.window().frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(
                event.globalPosition().toPoint() - self._drag_pos
            )
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class TerminalView(QTextEdit):
    """A single scrolling terminal-style text stream.

    The prompt and input are the last line of the document. The command output is inserted
    above the input line, then a new prompt is drawn, so the input line
    "descends" along with the accumulated output and is always visible at the bottom.
    The up/down arrows and Enter are handled by the BindsManager (history).
    """

    PROMPT = "~ > "  # the text part of the invitation (for parsing); the color is specified separately

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._binds = BindsManager(self)
        # Clicks are delivered to the viewport (not to the QTextEdit itself), so
        # We restrict the cursor using an event filter on the viewport.
        self._press_anchor = None
        self.viewport().installEventFilter(self)
        self._init_document()

    # --- Formats ---
    def _fmt(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def _insert_prompt(self, cursor):
        """Inserts a colored `~ > ` prompt at the cursor position."""
        cursor.insertText("~ ", self._fmt(DIM))
        cursor.insertText("> ", self._fmt(ACCENT))
        return cursor

    def _init_document(self):
        cursor = self.textCursor()
        self._insert_prompt(cursor)
        self.moveCursor(QTextCursor.MoveOperation.End)

    # --- Contract for BindsManager ---
    def get_input_text(self):
        """Returns the text of the current input line (without the prompt)."""
        block = self.document().lastBlock()
        text = block.text()
        if text.startswith(self.PROMPT):
            return text[len(self.PROMPT):]
        return text

    def set_input_text(self, text):
        """Replaces the text of the input line with `text`, cursor — at the end."""
        block = self.document().lastBlock()
        # We select only the block text, without its line break separator,
        # to avoid "eating" the line feed of the previous output block.
        start = block.position()
        end = start + block.length() - 1
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self._insert_prompt(cursor)
        cursor.insertText(text, self._fmt(FG))
        self.setTextCursor(cursor)

    def reset_input_text(self):
        self.set_input_text("")

    def _ensure_input_cursor(self):
        """Returns the cursor to the input line if it has moved to the output."""
        block = self.document().lastBlock()
        cursor = self.textCursor()
        if cursor.block() != block:
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def _prompt_boundary(self, block=None):
        """The position where the prompt ends and the editable input begins."""
        block = block or self.document().lastBlock()
        return block.position() + len(self.PROMPT)

    def _protect_prompt(self, event):
        """Protects the prompt from editing.

        Returns True if the keypress should be swallowed (not passed on),
        otherwise False - normal key handling.
        """
        key = event.key()
        cursor = self.textCursor()
        block = self.document().lastBlock()

        # We protect the prompt only on the input line; in the output, the cursor moves anyway.
        if cursor.block() != block:
            return False

        boundary = self._prompt_boundary(block)
        has_sel = cursor.hasSelection()
        sel_start = cursor.selectionStart()
        pos = cursor.position()

        if key == Qt.Key.Key_Backspace:
            # You can't delete a prompt either character by character or by selecting it,
            # which captures the beginning of the prompt.
            if has_sel:
                return sel_start < boundary
            return pos <= boundary

        if key == Qt.Key.Key_Delete:
            if has_sel:
                return sel_start < boundary
            # Delete deletes the character after the cursor - we don't allow deletion in the prompt area.
            return pos < boundary

        if key == Qt.Key.Key_Left:
            # We do not allow the cursor to move to the left of the input border.
            if not has_sel and pos <= boundary:
                return True
            return False

        if key == Qt.Key.Key_Home:
            # Home takes you to the beginning of the edited part, not to the prompt.
            cursor.setPosition(boundary)
            self.setTextCursor(cursor)
            return True

        # Other keys: prevent the cursor from remaining/inserting in the prompt area.
        if pos < boundary and not has_sel:
            cursor.setPosition(boundary)
            self.setTextCursor(cursor)
        return False

    def _input_editable_range(self, block=None):
        """The range (start, end) of the editable area of ​​the input line."""
        block = block or self.document().lastBlock()
        start = self._prompt_boundary(block)
        end = block.position() + block.length() - 1
        return start, end

    def eventFilter(self, obj, event):
        """Restricts the mouse to the input line (clicks and selections)."""
        if obj is self.viewport():
            et = event.type()
            if et == QEvent.Type.MouseButtonPress:
                self._handle_mouse_press(event)
                return True  # consume - QTextEdit does not put the cursor in the history
            if et == QEvent.Type.MouseButtonDblClick:
                self._handle_mouse_press(event)
                return True
            if et == QEvent.Type.MouseMove:
                self._handle_mouse_move(event)
                return True
            if et == QEvent.Type.MouseButtonRelease:
                return True
        return super().eventFilter(obj, event)

    def _handle_mouse_press(self, event):
        """Click: cursor should not fall into the output history or prompt zone."""
        block = self.document().lastBlock()
        start = self._prompt_boundary(block)
        end = block.position() + block.length() - 1

        cur = self.cursorForPosition(event.position().toPoint())
        if cur.block() != block:
            # Click in the history area - the cursor is at the end of the input line.
            pos = end
        elif cur.position() < start:
            # Click in the prompt area to the border of the editable input.
            pos = start
        else:
            pos = cur.position()

        cursor = QTextCursor(self.document())
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
        self._press_anchor = pos
        self.setFocus()

    def _handle_mouse_move(self, event):
        """Mouse selection is limited to the input line only."""
        block = self.document().lastBlock()
        start, end = self._input_editable_range(block)

        raw = self.cursorForPosition(event.position().toPoint()).position()
        pos = max(start, min(raw, end))

        cursor = QTextCursor(self.document())
        cursor.setPosition(self._press_anchor if self._press_anchor is not None else pos)
        cursor.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    # --- Keys ---
    def keyPressEvent(self, event):
        key = event.key()
        self._ensure_input_cursor()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # Navigate through command history.
            if self._binds.keyPressEvent(event):
                return
            super().keyPressEvent(event)
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # We reset navigation and execute the command (without inserting a line break).
            self._binds.keyPressEvent(event)
            self.execute_command()
            return

        if self._protect_prompt(event):
            return

        super().keyPressEvent(event)

    # --- Output / Execution ---
    def execute_command(self):
        user_input = self.get_input_text().strip()

        if not user_input:
            self.reset_input_text()
            return

        try:
            tag, message, cwd = Hexer.handle_command(user_input)
        except Exception as error:
            message = f"Error: {error}"
            tag = "error"

        # Special commands processed on the GUI side.
        if tag == "exit":
            # Correct termination of the application.
            self.window().close()
            return
        if tag == "clear":
            # Clears the entire output area, leaving only the prompt.
            self.clear_screen()
            return

        # All errors (unknown command, invalid arguments, exceptions
        # etc.) are output in red through a single print_error.
        if tag == "error":
            self.print_error(message)
        else:
            self._append_output(message if message else "")

    def clear_screen(self):
        """Clears the output area completely and leaves only the prompt."""
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.removeSelectedText()
        self._init_document()
        self.moveCursor(QTextCursor.MoveOperation.End)

    def _append_output(self, text, color=None):
        """Inserts output above the input line and draws a new prompt below it.

        If `color` is specified, the output text is colored in that color (for errors -
        muted red), otherwise - normal color.
        """
        cursor = QTextCursor(self.document().lastBlock())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.beginEditBlock()
        if text:
            cursor.insertText("\n")
            cursor.insertText(text, self._fmt(color or FG))
            cursor.insertText("\n")
        else:
            cursor.insertText("\n")
        self._insert_prompt(cursor)
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.ensureCursorVisible()

    def print_error(self, text):
        """Single point of error output - in red."""
        self._append_output(text, ERR)


class HexerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hexer")
        # Without the standard OS frame, we draw our own title bar.
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(200, 200, 900, 560)

        self.init_ui()
        self.setWindowIcon(QIcon("/app/share/icons/hicolor/512x512/apps/com.teambasert.Hexer.png"))

        # Hotkey F11 - toggle full screen.
        QShortcut(QKeySequence(Qt.Key.Key_F11), self, activated=self.toggle_fullscreen)

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Свой тайтл-бар сверху.
        self.title_bar = TitleBar("~ - Hexer", self)
        root.addWidget(self.title_bar)

        # Single terminal field: prompt + output + input in one stream.
        self.terminal = TerminalView()
        self.terminal.setFont(QFont(MONO, 13))
        self.terminal.setStyleSheet(
            "QTextEdit {"
            "  background: transparent;"
            "  border: none;"
            f"  color: {FG};"
            "  selection-background-color: #3b3b3b;"
            "}"
        )

        body = QVBoxLayout()
        body.setContentsMargins(14, 8, 14, 12)
        body.setSpacing(6)
        body.addWidget(self.terminal, 1)
        root.addLayout(body, 1)

        self.setStyleSheet(f"background-color: {BG};")

    def showEvent(self, event):
        super().showEvent(event)
        # With a frameless window, Qt does not set focus automatically -
        # We activate the window and move the focus to the terminal.
        self.activateWindow()
        self.terminal.setFocus()

    def toggle_fullscreen(self):
        """Toggles full screen mode (button in the title bar or F11)."""
        if self.isFullScreen():
            self.showNormal()
            self.title_bar.set_fullscreen_state(False)
        else:
            self.showFullScreen()
            self.title_bar.set_fullscreen_state(True)


def run_gui():
    app = QApplication(sys.argv)

    window = HexerGUI()
    window.show()

    sys.exit(app.exec())
