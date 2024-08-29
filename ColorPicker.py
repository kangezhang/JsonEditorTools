from PySide6.QtWidgets import QMainWindow, QColorDialog, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QScreen, QColor, QCursor
from PySide6.QtCore import Qt


class ColorPickerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.color_label = QLabel('No color selected', self)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(self.color_label)

        select_button = QPushButton('Select Color', self)
        select_button.clicked.connect(self.open_color_dialog)
        layout.addWidget(select_button)

        pick_button = QPushButton('Pick Color From Screen', self)
        pick_button.clicked.connect(self.pick_color)
        layout.addWidget(pick_button)

        self.setLayout(layout)

    def open_color_dialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.display_color(color)

    def pick_color(self):
        screen = QScreen.grabWindow(QApplication.primaryScreen(), QApplication.desktop().winId())
        color = QColor(screen.toImage().pixel(self.mapFromGlobal(QCursor.pos())))
        self.display_color(color)

    def display_color(self, color):
        hex_color = color.name()
        rgb_color = f'RGB: {color.red()}, {color.green()}, {color.blue()}'
        hsv_color = f'HSV: {color.hue()}, {color.saturation()}, {color.value()}'

        self.color_label.setText(f'Selected Color: {hex_color}\n{rgb_color}\n{hsv_color}')
        self.color_label.setStyleSheet(f'background-color: {hex_color};')

    def get_color_data(self):
        text = self.color_label.text().split('\n')
        return {
            "hex": text[1].split(': ')[1],
            "rgb": text[2].split(': ')[1],
            "hsv": text[3].split(': ')[1],
        }


class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Color Picker App')

        self.color_picker_widget = ColorPickerWidget()
        self.setCentralWidget(self.color_picker_widget)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    mainWin = ColorPickerApp()
    mainWin.show()

    sys.exit(app.exec())
