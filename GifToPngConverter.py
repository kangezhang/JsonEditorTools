from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit
from PySide6.QtCore import Qt
import sys
import os

class GifToPngConverter:
    def __init__(self, frame_rate=30):
        self.frame_rate = frame_rate

    def convert(self, gif_path, output_dir, frame_name_template="frame_{index}.png"):
        from PIL import Image  # 延迟导入Pillow以避免未安装时出错
        gif = Image.open(gif_path)
        os.makedirs(output_dir, exist_ok=True)
        duration_per_frame = int(1000 / self.frame_rate)
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_image = gif.convert("RGBA")
            output_file_name = frame_name_template.format(index=frame)
            output_file_path = os.path.join(output_dir, output_file_name)
            frame_image.save(output_file_path)
            gif.info['duration'] = duration_per_frame
        print(f"GIF 转换为 PNG 序列完成！所有帧已保存到: {output_dir}")

class GifConverterPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('GIF to PNG Converter')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # GIF文件选择
        self.gif_label = QLabel("Select GIF File:")
        self.gif_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.gif_label)

        self.gif_path_edit = QLineEdit()
        layout.addWidget(self.gif_path_edit)

        self.gif_browse_button = QPushButton("Browse...")
        self.gif_browse_button.clicked.connect(self.browse_gif)
        layout.addWidget(self.gif_browse_button)

        # 输出目录选择
        self.output_label = QLabel("Select Output Directory:")
        self.output_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.output_label)

        self.output_path_edit = QLineEdit()
        layout.addWidget(self.output_path_edit)

        self.output_browse_button = QPushButton("Browse...")
        self.output_browse_button.clicked.connect(self.browse_output_dir)
        layout.addWidget(self.output_browse_button)

        # 自定义文件名模板
        self.template_label = QLabel("Frame Name Template (e.g., frame_{index}.png):")
        self.template_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.template_label)

        self.template_edit = QLineEdit("frame_{index}.png")
        layout.addWidget(self.template_edit)

        # 转换按钮
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_gif)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)

    def browse_gif(self):
        gif_file, _ = QFileDialog.getOpenFileName(self, "Select GIF File", "", "GIF Files (*.gif)")
        if gif_file:
            self.gif_path_edit.setText(gif_file)

    def browse_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            self.output_path_edit.setText(output_dir)

    def convert_gif(self):
        gif_path = self.gif_path_edit.text()
        output_dir = self.output_path_edit.text()
        frame_name_template = self.template_edit.text()

        if gif_path and output_dir and frame_name_template:
            converter = GifToPngConverter(frame_rate=30)
            converter.convert(gif_path, output_dir, frame_name_template)
        else:
            print("Please fill in all fields.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = GifConverterPanel()
    panel.show()
    sys.exit(app.exec())
