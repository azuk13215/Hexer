import sys
from core.command import Hexer
from binds.binds import BindsManager
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QLabel,
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon


class HistoryLineEdit(QLineEdit):
    """Поле ввода, делегирующее обработку горячих клавиш в BindsManager."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._binds = BindsManager(self)

    def keyPressEvent(self, event):
        # Горячие клавиши (стрелки, Enter) обрабатывает BindsManager.
        # Если он вернул True — клавиша обработана, стандартную обработку пропускаем.
        if self._binds.keyPressEvent(event):
            return

        # Остальные клавиши (Backspace и т.д.) — стандартное поведение.
        super().keyPressEvent(event)

class HexerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hexer")
        self.setGeometry(200, 200, 1000, 600)

        self.init_ui()
        self.setWindowIcon(QIcon("/app/share/icons/hicolor/512x512/apps/com.teambasert.Hexer.png"))

    def init_ui(self):
        layout = QVBoxLayout()

        # Heading
        title = QLabel("HEXER TERMINAL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #00ff99;"
            "font-size: 24px;"
            "font-weight: bold;"
            "padding: 10px;"
        )

        # Terminal output field
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 11))
        self.terminal_output.setStyleSheet(
            "background-color: #0d1117;"
            "color: #00ff99;"
            "border: 2px solid #00ff99;"
            "padding: 10px;"
        )

        self.terminal_output.append("Welcome to Hexer GUI")
        self.terminal_output.append("Type 'help' to see commands.\n")

        # Input field
        self.command_input = HistoryLineEdit()
        self.command_input.setFont(QFont("Consolas", 11))
        self.command_input.setStyleSheet(
            "background-color: #161b22;"
            "color: white;"
            "border: 2px solid #00ff99;"
            "padding: 8px;"
        )
        self.command_input.setPlaceholderText("Enter command...")
        self.command_input.returnPressed.connect(self.execute_command)

        layout.addWidget(title)
        layout.addWidget(self.terminal_output)
        layout.addWidget(self.command_input)

        self.setLayout(layout)

        self.setStyleSheet("background-color: #010409;")

    def execute_command(self):
        user_input = self.command_input.text().strip()

        if not user_input:
            return

        self.terminal_output.append(f"> {user_input}")

        try:
            tag, message, cwd = Hexer.handle_command(user_input)

            if message:
                self.terminal_output.append(message)

        except Exception as error:
            self.terminal_output.append(f"Error: {error}")


        self.command_input.clear()

def run_gui():
    app = QApplication(sys.argv)

    window = HexerGUI()
    window.show()

    sys.exit(app.exec())
