import os
import json

from PyQt6.QtCore import Qt


class BindsManager:
    """Управление горячими клавишами и навигацией по истории команд.

    Содержит логику обработки стрелок вверх/вниз и Enter в поле ввода.
    Состояние и логика перенесены из HistoryLineEdit (core/gui.py).
    """

    HISTORY_FILE = os.path.expanduser(
        "/home/andriy/Hexer/Hexer/data/hexer_history.json"
    )

    def __init__(self, widget):
        self.widget = widget

        # Список команд истории: от самой старой к самой новой.
        # Берём те же данные, что пишутся в JSON (формат: список {id, command}).
        self._history = self._load_history()

        # Индекс текущей позиции. len(_history) — "новая" позиция (пустое поле),
        # от которой пользователь начинает листать историю.
        self._history_index = len(self._history)

        # Черновик: текст, который пользователь начал печатать до листания.
        self._draft = ""

    def _load_history(self):
        """Читает историю из того же JSON-файла, что использует остальной код."""
        try:
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Данные — список объектов {id, command}; извлекаем только команды.
            commands = []
            for item in data:
                cmd = item.get("command") if isinstance(item, dict) else item
                if cmd:
                    commands.append(str(cmd))
            return commands
        except (OSError, ValueError):
            return []

    def _apply_text(self, text):
        """Подставляет команду в поле и ставит курсор в конец."""
        self.widget.setText(text)
        self.widget.setCursorPosition(len(text))

    def keyPressEvent(self, event):
        """Обрабатывает горячую клавишу.

        Возвращает True, если клавиша обработана и дальше передавать не нужно,
        иначе False — чтобы виджет обработал её стандартно (например, Enter).
        """
        key = event.key()

        if key == Qt.Key.Key_Up:
            self._navigate_older()
            return True
        if key == Qt.Key.Key_Down:
            self._navigate_newer()
            return True
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Команда выполнена — сбрасываем навигацию в начальное состояние.
            self._reset_navigation()

        return False

    def _navigate_older(self):
        """Стрелка вверх: предыдущая (более старая) команда из истории."""
        if not self._history:
            return

        if self._history_index == len(self._history):
            # Только начинаем листать — запоминаем текущий черновик.
            self._draft = self.widget.text()
            self._history_index -= 1
        elif self._history_index > 0:
            self._history_index -= 1
        else:
            return  # уже на самой старой команде

        self._apply_text(self._history[self._history_index])

    def _navigate_newer(self):
        """Стрелка вниз: более новая команда; в конце — черновик / пустое поле."""
        if self._history_index == len(self._history):
            return  # уже в конце, дальше некуда

        self._history_index += 1

        if self._history_index == len(self._history):
            # Дошли до конца истории — восстанавливаем черновик.
            draft, self._draft = self._draft, ""
            self._apply_text(draft)
        else:
            self._apply_text(self._history[self._history_index])

    def _reset_navigation(self):
        """Возвращает навигацию в начальное состояние после выполнения команды."""
        # Перечитываем историю, чтобы в неё попали только что введённые команды.
        self._history = self._load_history()

        self._history_index = len(self._history)
        self._draft = ""
