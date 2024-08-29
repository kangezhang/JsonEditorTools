from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox,
                               QSpinBox, QFileDialog, QCheckBox, QHBoxLayout)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal
import os
import time
from PIL import Image


class GifToPngConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.play_animation = False
        self.frame_rate = 30
        self.loop_animation = True
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Contact Sheet Creator')
        self.setFixedSize(560, 700)

        layout = QVBoxLayout()

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Contact Sheet", "Animation"])
        self.mode_selector.currentIndexChanged.connect(self.switch_mode)
        layout.addWidget(self.mode_selector)

        # Contact sheet controls
        self.contact_sheet_controls = QWidget()
        contact_sheet_layout = QVBoxLayout()

        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_files)
        contact_sheet_layout.addWidget(self.select_folder_button)

        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("Rows:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 10)
        self.rows_spinbox.setValue(4)
        grid_layout.addWidget(self.rows_spinbox)
        grid_layout.addWidget(QLabel("Columns:"))
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setRange(1, 10)
        self.columns_spinbox.setValue(4)
        grid_layout.addWidget(self.columns_spinbox)
        contact_sheet_layout.addLayout(grid_layout)

        image_size_layout = QHBoxLayout()
        image_size_layout.addWidget(QLabel("Image Size:"))
        self.image_size_combo = QComboBox()
        self.image_size_combo.addItems(["1024", "2048", "4096"])
        self.image_size_combo.setCurrentText("1024")
        image_size_layout.addWidget(self.image_size_combo)
        contact_sheet_layout.addLayout(image_size_layout)

        preview_save_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_contact_sheet)
        preview_save_layout.addWidget(self.preview_button)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_contact_sheet)
        preview_save_layout.addWidget(self.save_button)
        contact_sheet_layout.addLayout(preview_save_layout)

        self.contact_sheet_controls.setLayout(contact_sheet_layout)
        layout.addWidget(self.contact_sheet_controls)

        # Animation controls
        self.animation_controls = QWidget()
        animation_layout = QVBoxLayout()

        self.select_folder_button_anim = QPushButton("Select Folder")
        self.select_folder_button_anim.clicked.connect(self.select_files)
        animation_layout.addWidget(self.select_folder_button_anim)

        frame_rate_layout = QHBoxLayout()
        frame_rate_layout.addWidget(QLabel("Frame Rate:"))
        self.frame_rate_spinbox = QSpinBox()
        self.frame_rate_spinbox.setRange(1, 60)
        self.frame_rate_spinbox.setValue(30)
        frame_rate_layout.addWidget(self.frame_rate_spinbox)
        animation_layout.addLayout(frame_rate_layout)

        self.loop_checkbox = QCheckBox("Loop Animation")
        self.loop_checkbox.setChecked(True)
        animation_layout.addWidget(self.loop_checkbox)

        start_stop_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Animation")
        self.start_button.clicked.connect(self.start_animation)
        start_stop_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        start_stop_layout.addWidget(self.stop_button)
        animation_layout.addLayout(start_stop_layout)

        self.animation_controls.setLayout(animation_layout)
        self.animation_controls.setVisible(False)
        layout.addWidget(self.animation_controls)

        # Preview area
        layout.addWidget(QLabel("Preview Window:"))
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(420, 420)
        layout.addWidget(self.preview_label)

        self.setLayout(layout)

    def select_files(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.selected_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(self.selected_files)

    def switch_mode(self):
        mode = self.mode_selector.currentText()
        if mode == "Contact Sheet":
            self.contact_sheet_controls.setVisible(True)
            self.animation_controls.setVisible(False)
        elif mode == "Animation":
            self.contact_sheet_controls.setVisible(False)
            self.animation_controls.setVisible(True)

    def create_contact_sheet(self):
        if not self.selected_files:
            print("No files selected")
            return None

        rows = self.rows_spinbox.value()
        columns = self.columns_spinbox.value()
        size = int(self.image_size_combo.currentText())

        if rows * columns < len(self.selected_files):
            print("Error: Rows * Columns must be greater than or equal to the number of selected images.")
            return None

        images = [Image.open(file) for file in self.selected_files]

        img_width, img_height = images[0].size
        scale = size / max(img_width * columns, img_height * rows)
        images = [img.resize((int(img_width * scale), int(img_height * scale)), Image.Resampling.LANCZOS) for img in images]

        contact_sheet = Image.new(images[0].mode, (columns * images[0].width, rows * images[0].height))
        for index, img in enumerate(images):
            x = index % columns * img.width
            y = index // columns * img.height
            contact_sheet.paste(img, (x, y))

        return contact_sheet

    def preview_contact_sheet(self):
        contact_sheet = self.create_contact_sheet()
        if contact_sheet:
            contact_sheet.thumbnail((420, 420))
            contact_sheet.save("preview.png")
            self.preview_label.setPixmap(QPixmap("preview.png"))

    def save_contact_sheet(self):
        contact_sheet = self.create_contact_sheet()
        if contact_sheet:
            contact_sheet.save("contact_sheet.png")
            print("Contact sheet created and saved as 'contact_sheet.png'")

    def start_animation(self):
        self.play_animation = True
        self.frame_rate = self.frame_rate_spinbox.value()
        self.loop_animation = self.loop_checkbox.isChecked()

        self.animation_thread = AnimationThread(self.selected_files, self.frame_rate, self.loop_animation, self.preview_label)
        self.animation_thread.start()

    def stop_animation(self):
        self.play_animation = False
        if hasattr(self, 'animation_thread'):
            self.animation_thread.stop()

class AnimationThread(QThread):
    def __init__(self, selected_files, frame_rate, loop_animation, preview_label):
        super().__init__()
        self.selected_files = selected_files
        self.frame_rate = frame_rate
        self.loop_animation = loop_animation
        self.preview_label = preview_label
        self.play_animation = True

    def run(self):
        frame_interval = 1.0 / self.frame_rate
        while self.play_animation:
            for file in self.selected_files:
                if not self.play_animation:
                    break
                image = QImage(file)
                pixmap = QPixmap.fromImage(image.scaled(self.preview_label.size(), Qt.KeepAspectRatio))
                self.preview_label.setPixmap(pixmap)
                time.sleep(frame_interval)
            if not self.loop_animation:
                break

    def stop(self):
        self.play_animation = False
        self.quit()


if __name__ == "__main__":
    app = QApplication([])

    window = GifToPngConverter()
    window.show()

    app.exec()
