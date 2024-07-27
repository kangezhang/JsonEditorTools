import dearpygui.dearpygui as dpg
from PIL import Image
import os
import shutil
import platform
import subprocess

# 全局变量
image_list = []
rows = 4
columns = 4
image_size = 160
undo_stack = []
supported_formats = ['png', 'jpg', 'jpeg', 'tga', 'tiff']

# 更新图片网格显示
def update_image_grid():
    global image_list, rows, columns
    dpg.delete_item("image_grid", children_only=True)
    
    with dpg.group(horizontal=False, parent="image_grid"):
        for r in range(rows):
            with dpg.group(horizontal=True):
                for c in range(columns):
                    idx = r * columns + c
                    if idx < len(image_list):
                        image_path = image_list[idx]
                        file_name, file_extension = os.path.splitext(os.path.basename(image_path))
                        file_extension = file_extension.lstrip('.')
                        with Image.open(image_path) as img:
                            img.thumbnail((image_size, image_size))
                            img.save("temp_thumbnail.png")
                            width, height, channels, data = dpg.load_image("temp_thumbnail.png")
                            with dpg.texture_registry(show=False):
                                texture_id = dpg.add_static_texture(width, height, data)
                            with dpg.group(horizontal=False):
                                dpg.add_image(texture_id, tag=f"image_{idx}")
                                with dpg.popup(f"image_{idx}", mousebutton=dpg.mvMouseButton_Right):
                                    dpg.add_button(label="Show in Explorer", callback=show_in_explorer, user_data=image_path)
                                dpg.add_input_text(default_value=file_name, callback=rename_image_callback, user_data=(idx, "name"), width=150, on_enter=True, tag=f"image_{idx}_name")
                                with dpg.group(horizontal=True):
                                    if file_extension in supported_formats:
                                        dpg.add_combo(supported_formats, default_value=file_extension, callback=rename_image_callback, user_data=(idx, "format"), width=75, tag=f"image_{idx}_format")
                                    else:
                                        dpg.add_text(file_extension, tag=f"image_{idx}_format")
                                    dpg.add_button(label="Save", callback=save_image_callback, user_data=idx, tag=f"save_{idx}")

# 重命名图片的回调函数
def rename_image_callback(sender, app_data, user_data):
    global image_list, undo_stack
    index, field = user_data
    old_path = image_list[index]
    file_name, file_extension = os.path.splitext(os.path.basename(old_path))
    directory = os.path.dirname(old_path)
    
    if field == "name":
        new_name = app_data
        new_path = os.path.join(directory, new_name + file_extension)
    elif field == "format":
        new_format = app_data
        new_path = os.path.join(directory, file_name + '.' + new_format)
    
    if not os.path.exists(new_path):  # 避免文件名冲突
        shutil.move(old_path, new_path)
        image_list[index] = new_path
        undo_stack.append((old_path, new_path))
    else:
        if field == "name":
            dpg.set_value(sender, file_name)  # 恢复旧名称
        elif field == "format":
            dpg.set_value(sender, file_extension.lstrip('.'))  # 恢复旧格式

# 导入图片的回调函数
def import_images_callback(sender, app_data):
    global image_list
    folder_path = app_data['file_path_name']
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tga', '.tiff')):
            image_list.append(os.path.join(folder_path, file_name))
    update_image_grid()

# 行和列输入框的回调函数
def update_grid_dimensions(sender, app_data):
    global rows, columns
    if sender == "rows_input":
        rows = app_data
    elif sender == "columns_input":
        columns = app_data
    update_image_grid()

# 调整图片大小的回调函数
def update_image_size(sender, app_data):
    global image_size
    image_size = app_data
    update_image_grid()

# 保存图片的回调函数
def save_image_callback(sender, app_data, user_data):
    global image_list, undo_stack
    index = user_data
    if index is None:
        return  # 防止 user_data 为空
    
    image_path = image_list[index]
    new_name = dpg.get_value(f"image_{index}_name")
    new_format = dpg.get_value(f"image_{index}_format")
    directory = os.path.dirname(image_path)
    save_path = os.path.join(directory, new_name + '.' + new_format)

    if not os.path.exists(save_path):  # 避免文件名冲突
        shutil.move(image_path, save_path)
        undo_stack.append((save_path, image_path))
        image_list[index] = save_path
        print(f"Image saved as {save_path}")
    else:
        print(f"File {save_path} already exists!")

# 撤销重命名操作的回调函数
def undo_rename():
    global undo_stack
    if undo_stack:
        new_path, old_path = undo_stack.pop()
        shutil.move(new_path, old_path)
        index = image_list.index(new_path)
        image_list[index] = old_path
        update_image_grid()

# 持续监听按键事件
def key_press_callback(sender, app_data):
    if platform.system() == 'Darwin':  # Mac系统
        if dpg.is_key_down(dpg.mvKey_Z) and dpg.is_key_down(dpg.mvKey_Super):
            undo_rename()
    else:  # Windows和其他系统
        if dpg.is_key_down(dpg.mvKey_Z) and dpg.is_key_down(dpg.mvKey_Control):
            undo_rename()

# 显示在资源管理器中并高亮显示文件
def show_in_explorer(sender, app_data, user_data):
    file_path = user_data
    if platform.system() == "Windows":
        subprocess.run(f'explorer /select,"{file_path}"')
    elif platform.system() == "Darwin":
        subprocess.run(["open", "-R", file_path])
    else:
        subprocess.run(["xdg-open", os.path.dirname(file_path)])

# 创建DearPyGui用户界面
dpg.create_context()

# 创建主要窗口和图片网格
with dpg.window(label="Image Manager", width=600, height=600, no_move=True, no_resize=True, no_close=True, no_collapse=True, tag="main_window"):
    # 创建菜单栏
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Import", callback=lambda: dpg.show_item("file_dialog"))
        with dpg.menu(label="Edit"):
            dpg.add_menu_item(label="Undo Rename", callback=undo_rename)

    with dpg.group(horizontal=True):
        dpg.add_text("Rows:")
        dpg.add_input_int(default_value=4, min_value=1, max_value=10, width=100, callback=update_grid_dimensions, tag="rows_input")
        dpg.add_text("Columns:")
        dpg.add_input_int(default_value=4, min_value=1, max_value=10, width=100, callback=update_grid_dimensions, tag="columns_input")
        dpg.add_text("Image Size:")
        dpg.add_slider_int(default_value=160, min_value=50, max_value=200, width=100, callback=update_image_size, tag="image_size_slider")
    
    with dpg.child_window(autosize_x=True, autosize_y=True, tag="image_grid"):
        pass

# 创建文件选择器对话框
with dpg.file_dialog(directory_selector=True, show=False, callback=import_images_callback, tag="file_dialog"):
    dpg.add_file_extension(".*")

# 设置系统窗口
def resize_callback(sender, app_data):
    width, height = dpg.get_viewport_client_width(), dpg.get_viewport_client_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)

dpg.create_viewport(title='Image Manager', width=800, height=600, resizable=True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_viewport_resize_callback(resize_callback)

# 每帧回调函数
def frame_callback(sender, app_data):
    key_press_callback(sender, app_data)
    dpg.set_frame_callback(1, frame_callback)

# 初始调整窗口大小
resize_callback(None, None)

# 设置每帧回调
dpg.set_frame_callback(1, frame_callback)

dpg.start_dearpygui()
dpg.destroy_context()
