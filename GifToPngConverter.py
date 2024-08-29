from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                               QFileDialog, QSpinBox, QLineEdit, QHBoxLayout)
from PySide6.QtCore import Qt
from PIL import Image
import os


class GifToPngConverter:
    def __init__(self):
        self.input_frame_rate = None
        self.output_frame_rate = None

    def get_gif_frame_rate(self, gif):
        total_frames = gif.n_frames
        durations = []

        for frame in range(total_frames):
            gif.seek(frame)
            try:
                duration = gif.info['duration']  # 获取当前帧的持续时间（ms）
                durations.append(duration)
            except KeyError:
                durations.append(100)  # 如果没有指定持续时间，默认为100ms

        avg_duration = sum(durations) / len(durations)
        frame_rate = 1000 / avg_duration  # 每秒帧数 (fps)

        return frame_rate

    def convert(self, gif_path, output_dir, output_frame_rate, frame_name_template="frame_{index}.png"):
        gif = Image.open(gif_path)
        os.makedirs(output_dir, exist_ok=True)

        # 获取输入的帧速率
        self.input_frame_rate = self.get_gif_frame_rate(gif)
        self.output_frame_rate = float(output_frame_rate)
        print(f"Detected GIF frame rate: {self.input_frame_rate:.2f} fps")
        print(f"Output GIF frame rate: {self.output_frame_rate:.2f} fps")

        # 计算帧插值比例
        frame_ratio = self.output_frame_rate / self.input_frame_rate
        frame = 0
        output_frame = 0

        while True:
            try:
                gif.seek(frame)
                frame_image = gif.convert('RGBA')  # 转换为 RGBA 模式以支持透明度

                # 使用高质量的缩放方法减少锯齿
                frame_image = frame_image.resize(frame_image.size, Image.Resampling.LANCZOS)

                # 根据插值比例生成新的帧
                while output_frame < (frame + 1) * frame_ratio:
                    output_file_name = frame_name_template.format(index=int(output_frame))
                    output_file_path = os.path.join(output_dir, output_file_name)

                    # 保存帧为PNG格式，保证输出质量
                    frame_image.save(output_file_path, optimize=True, quality=95)

                    output_frame += 1

                frame += 1
            except EOFError:
                break

        print(f"GIF 转换为 PNG 序列完成！所有帧已保存到: {output_dir}")


class GifConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GIF to PNG Converter")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        # GIF文件选择
        self.gif_label = QLabel("Select GIF File:")
        layout.addWidget(self.gif_label)

        self.gif_path_edit = QLineEdit()
        layout.addWidget(self.gif_path_edit)

        self.gif_browse_button = QPushButton("Browse...")
        self.gif_browse_button.clicked.connect(self.browse_gif)
        layout.addWidget(self.gif_browse_button)

        # 输出目录选择
        self.output_label = QLabel("Select Output Directory:")
        layout.addWidget(self.output_label)

        self.output_path_edit = QLineEdit()
        layout.addWidget(self.output_path_edit)

        self.output_browse_button = QPushButton("Browse...")
        self.output_browse_button.clicked.connect(self.browse_output_dir)
        layout.addWidget(self.output_browse_button)

        # 输出帧率设置
        self.frame_rate_layout = QHBoxLayout()
        self.frame_rate_label = QLabel("Output Frame Rate:")
        self.frame_rate_spinbox = QSpinBox()
        self.frame_rate_spinbox.setRange(1, 60)
        self.frame_rate_spinbox.setValue(30)
        self.frame_rate_layout.addWidget(self.frame_rate_label)
        self.frame_rate_layout.addWidget(self.frame_rate_spinbox)
        layout.addLayout(self.frame_rate_layout)

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
        output_frame_rate = self.frame_rate_spinbox.value()

        if gif_path and output_dir:
            converter = GifToPngConverter()
            converter.convert(gif_path, output_dir, output_frame_rate)
        else:
            print("Please fill in all fields.")


if __name__ == "__main__":
    app = QApplication([])

    window = GifConverterGUI()
    window.show()

    app.exec()
