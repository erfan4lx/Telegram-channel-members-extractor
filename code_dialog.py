from PyQt6.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout, QStyle, QApplication
from PyQt6.QtCore import Qt

class CodeDialog(QDialog):
    def __init__(self, title="Enter Code", label="Code:", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText(label)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_value(self):
        return self.input.text()


class AsyncMessageBox(QDialog):
    def __init__(self, title, message, icon=QMessageBox.Icon.Information, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.result = None
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Dialog)

        layout = QVBoxLayout(self)

        # Left icon
        icon_label = QLabel()
        style = QApplication.style()
        if icon == QMessageBox.Icon.Critical:
            std_icon = QStyle.StandardPixmap.SP_MessageBoxCritical
        elif icon == QMessageBox.Icon.Warning:
            std_icon = QStyle.StandardPixmap.SP_MessageBoxWarning
        elif icon == QMessageBox.Icon.Question:
            std_icon = QStyle.StandardPixmap.SP_MessageBoxQuestion
        else:
            std_icon = QStyle.StandardPixmap.SP_MessageBoxInformation
        pixmap = style.standardIcon(std_icon).pixmap(48, 48)
        icon_label.setPixmap(pixmap)

        # Message text
        text_label = QLabel(message)
        text_label.setWordWrap(True)

        # Putting icons and text together
        hlayout = QHBoxLayout()
        hlayout.addWidget(icon_label)
        hlayout.addWidget(text_label)
        layout.addLayout(hlayout)

        # OK button
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setDefault(True)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignRight)

        # self.setFixedSize(400, 150)

    def on_ok(self):
        self.result = QMessageBox.StandardButton.Ok
        self.accept()

    def get_result(self):
        return self.result
