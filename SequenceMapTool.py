import dearpygui.dearpygui as dpg
from PIL import Image
import os
import time
import threading

# 全局变量用于存储选择的文件路径和动画参数
selected_files = []
play_animation = False
frame_rate = 30
loop_animation = True

# 文件选择器回调函数
def callback_function(sender, app_data):
    global selected_files
    selected_files = []
    folder_path = app_data['file_path_name']
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            selected_files.append(os.path.join(folder_path, file_name))
    print(selected_files)

# 选择文件按钮的回调函数
def select_files(sender, app_data):
    with dpg.file_dialog(directory_selector=True, width=420, height=220, show=True, callback=callback_function):
        dpg.add_file_extension(".*")

# 创建联系表的函数
def create_contact_sheet():
    global selected_files
    if not selected_files:
        print("No files selected")
        return None
    
    # 获取行数和列数以及图像大小
    rows = dpg.get_value("rows")
    columns = dpg.get_value("columns")
    size = int(dpg.get_value("image_size"))

    if rows * columns < len(selected_files):
        print("Error: Rows * Columns must be greater than or equal to the number of selected images.")
        return None
    
    images = [Image.open(file) for file in selected_files]
    
    # 假设所有图像大小相同
    img_width, img_height = images[0].size
    
    # 计算缩放比例
    scale = size / max(img_width * columns, img_height * rows)
    
    # 缩放图像
    images = [img.resize((int(img_width * scale), int(img_height * scale)), Image.Resampling.LANCZOS) for img in images]
    
    # 创建空白阵列图
    contact_sheet = Image.new(images[0].mode, (columns * images[0].width, rows * images[0].height))
    
    # 粘贴图像
    for index, img in enumerate(images):
        x = index % columns * img.width
        y = index // columns * img.height
        contact_sheet.paste(img, (x, y))
    
    return contact_sheet

# 预览按钮的回调函数
def preview_contact_sheet(sender, app_data):
    contact_sheet = create_contact_sheet()
    if contact_sheet:
        contact_sheet.thumbnail((420, 420))
        contact_sheet.save("preview.png")

        # 删除旧纹理和旧图像
        if dpg.does_item_exist("preview_texture"):
            dpg.delete_item("preview_texture")
        if dpg.does_item_exist("preview_image_display"):
            dpg.delete_item("preview_image_display")

        # 添加新纹理
        width, height, channels, data = dpg.load_image("preview.png")
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="preview_texture")
        
        # 添加新图像
        dpg.add_image("preview_texture", parent="preview_window", tag="preview_image_display")

# 保存按钮的回调函数
def save_contact_sheet(sender, app_data):
    contact_sheet = create_contact_sheet()
    if contact_sheet:
        contact_sheet.save("contact_sheet.png")
        print("Contact sheet created and saved as 'contact_sheet.png'")

# 动画播放线程函数
def play_animation_thread():
    global play_animation, frame_rate, loop_animation, selected_files
    frame_interval = 1.0 / frame_rate

    while play_animation:
        for file in selected_files:
            if not play_animation:
                break

            # 删除旧纹理和旧图像
            if dpg.does_item_exist("preview_texture"):
                dpg.delete_item("preview_texture")
            if dpg.does_item_exist("preview_image_display"):
                dpg.delete_item("preview_image_display")

            # 添加新纹理
            width, height, channels, data = dpg.load_image(file)
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag="preview_texture")
            
            # 添加新图像
            dpg.add_image("preview_texture", parent="preview_window", tag="preview_image_display")

            time.sleep(frame_interval)

        if not loop_animation:
            break

# 开始动画播放
def start_animation(sender, app_data):
    global play_animation, frame_rate, loop_animation
    play_animation = True
    frame_rate = dpg.get_value("frame_rate")
    loop_animation = dpg.get_value("loop_animation")

    animation_thread = threading.Thread(target=play_animation_thread)
    animation_thread.start()

# 停止动画播放
def stop_animation(sender, app_data):
    global play_animation
    play_animation = False

# 模式切换回调函数
def switch_mode(sender, app_data):
    mode = dpg.get_value("mode_selector")
    if mode == "Contact Sheet":
        dpg.show_item("contact_sheet_controls")
        dpg.hide_item("animation_controls")
    elif mode == "Animation":
        dpg.hide_item("contact_sheet_controls")
        dpg.show_item("animation_controls")

# 创建DearPyGui用户界面
dpg.create_context()

with dpg.texture_registry(show=False):
    # 初始化一个空的纹理
    dpg.add_static_texture(1, 1, [0, 0, 0, 0], tag="preview_texture")

window_width, window_height = 560, 700  # 主窗口大小

with dpg.window(label="Contact Sheet Creator", width=window_width, height=window_height, no_move=True, no_resize=True, no_close=True, no_collapse=True, no_title_bar=True):
    dpg.add_combo(label="Mode", items=["Contact Sheet", "Animation"], default_value="Contact Sheet", callback=switch_mode, tag="mode_selector")

    with dpg.group(horizontal=False, tag="contact_sheet_controls"):
        dpg.add_button(label="Select Folder", callback=select_files)
        with dpg.group(horizontal=True):
            dpg.add_text("Rows:")
            dpg.add_input_int(default_value=4, min_value=1, max_value=10, width=100, tag="rows")
            dpg.add_text("Columns:")
            dpg.add_input_int(default_value=4, min_value=1, max_value=10, width=100, tag="columns")
        with dpg.group(horizontal=True):
            dpg.add_text("Image Size:")
            dpg.add_combo(items=["1024", "2048", "4096"], default_value="1024", tag="image_size")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Preview", callback=preview_contact_sheet)
            dpg.add_button(label="Save", callback=save_contact_sheet)

    with dpg.group(horizontal=False, tag="animation_controls", show=False):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Select Folder", callback=select_files)
            dpg.add_text("Frame Rate:")
            dpg.add_input_int(default_value=30, min_value=1, max_value=60, width=100, tag="frame_rate")
            dpg.add_checkbox(label="Loop Animation", default_value=True, tag="loop_animation")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Animation", callback=start_animation)
            dpg.add_button(label="Stop Animation", callback=stop_animation)

    dpg.add_text("Preview Window:")
    with dpg.child_window(tag="preview_window", width=436, height=436):
        dpg.add_image("preview_texture", tag="preview_image_display", width=420, height=420)

# 设置系统窗口大小并禁止调整大小
dpg.create_viewport(title='Contact Sheet Creator', width=window_width, height=window_height, resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
