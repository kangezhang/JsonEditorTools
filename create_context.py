import dearpygui.dearpygui as dpg
import os

dpg.create_context()

recent_files = []


# Callback function for setting the image
def set_image_callback(sender, app_data, user_data):
    file_path = app_data["file_path_name"]
    if file_path and os.path.isfile(file_path):
        if file_path not in recent_files:
            recent_files.append(file_path)
            if len(recent_files) > 6:
                recent_files.pop(0)
        update_recent_files_menu()
        width, height, channels, data = dpg.load_image(file_path)
        if dpg.does_item_exist("loaded_texture"):
            dpg.delete_item("loaded_texture")
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="loaded_texture")
        dpg.configure_item("image_display", texture_tag="loaded_texture")


# Update recent files menu
def update_recent_files_menu():
    if dpg.does_item_exist("recent_files_menu"):
        dpg.delete_item("recent_files_menu", children_only=True)
    with dpg.menu(label="Recent Files", parent="recent_files_menu"):
        for file in recent_files:
            dpg.add_menu_item(label=file, callback=load_recent_file, user_data=file)


# Load recent file callback
def load_recent_file(sender, app_data, user_data):
    file_path = user_data
    if file_path and os.path.isfile(file_path):
        width, height, channels, data = dpg.load_image(file_path)
        if dpg.does_item_exist("loaded_texture"):
            dpg.delete_item("loaded_texture")
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag="loaded_texture")
        dpg.configure_item("image_display", texture_tag="loaded_texture")


# Callback function for the context menu item
def show_file_dialog(sender, app_data, user_data):
    dpg.show_item("file_dialog")


# Create a window
with dpg.window(label="Right-click to set image"):
    # Create a placeholder for the image
    with dpg.texture_registry():
        dpg.add_static_texture(1, 1, [255, 255, 255, 255], tag="default_texture")
    dpg.add_image("default_texture", tag="image_display", width=200, height=200)

    # Create a context menu
    with dpg.popup("image_display", mousebutton=dpg.mvMouseButton_Right):
        dpg.add_menu_item(label="Set Value", callback=show_file_dialog)
        with dpg.menu(label="Recent Files", tag="recent_files_menu"):
            update_recent_files_menu()

# Create a file dialog for selecting the image
with dpg.file_dialog(
    directory_selector=False, show=False, callback=set_image_callback, tag="file_dialog"
):
    dpg.add_file_extension(".png,.jpg,.jpeg")

dpg.create_viewport(title="Right-click Menu Example", width=400, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
