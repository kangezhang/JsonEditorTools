import os
import dearpygui.dearpygui as dpg
from PIL import Image


def select_folder_dialog(sender, app_data, user_data):
    dpg.show_item("file_dialog")


def folder_callback(sender, app_data, user_data):
    folder_path = app_data["file_path_name"].replace("\\", "/")
    dpg.set_value("folder_path_text", f"Selected Folder: {folder_path}")
    if os.path.isdir(folder_path):
        images = [
            os.path.join(folder_path, file).replace("\\", "/")
            for file in os.listdir(folder_path)
            if file.lower().endswith(("png", "jpg", "jpeg", "bmp", "gif"))
        ]
        valid_images = [img for img in images if os.path.isfile(img)]
        dpg.set_value("image_list", valid_images)
        print(f"Image List: {valid_images}")  # 打印调试信息


def preview_contact_sheet(sender, app_data, user_data):
    generate_contact_sheet(preview=True)


def save_contact_sheet(sender, app_data, user_data):
    generate_contact_sheet(preview=False)


def generate_contact_sheet(preview=True):
    images = dpg.get_value("image_list")
    print(f"Generating contact sheet with images: {images}")  # 打印调试信息
    columns = dpg.get_value("columns")
    rows = dpg.get_value("rows")
    size = 640

    if not images:
        print("No images found")
        return

    images_per_sheet = rows * columns
    contact_sheets = [
        images[i : i + images_per_sheet]
        for i in range(0, len(images), images_per_sheet)
    ]

    for idx, sheet_images in enumerate(contact_sheets):
        contact_sheet = Image.new("RGB", (size, size), (255, 255, 255))
        image_size = size // max(columns, rows)

        for i, img_path in enumerate(sheet_images):
            try:
                print(f"Opening image: {img_path}")  # 打印调试信息
                img = Image.open(img_path)
                img.thumbnail((image_size, image_size))
                x = (i % columns) * image_size
                y = (i // columns) * image_size
                contact_sheet.paste(img, (x, y))
            except Exception as e:
                print(f"Error opening image {img_path}: {e}")
                continue

        if preview:
            contact_sheet.save("preview.png")
            width, height, image_data = load_image("preview.png")
            dpg.set_value("contact_sheet_texture", image_data)
        else:
            contact_sheet.save(f"contact_sheet_{idx + 1}.png")
            print(f"Saved contact_sheet_{idx + 1}.png")


def load_image(file_path):
    try:
        image = Image.open(file_path)
        image = image.convert("RGBA")
        image_data = image.tobytes()
        width, height = image.size
        return width, height, image_data
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return 0, 0, None


def main():
    dpg.create_context()

    with dpg.file_dialog(
        directory_selector=True, show=False, callback=folder_callback, tag="file_dialog"
    ):
        dpg.add_file_extension(".*")

    with dpg.window(label="Image Contact Sheet Creator"):
        dpg.add_button(label="Select Folder", callback=select_folder_dialog)
        dpg.add_text("", tag="folder_path_text")

        dpg.add_text("Contact Sheet Settings:")
        dpg.add_input_int(label="Columns", tag="columns", default_value=5, min_value=1)
        dpg.add_input_int(label="Rows", tag="rows", default_value=5, min_value=1)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Preview", callback=preview_contact_sheet)
            dpg.add_button(label="Save", callback=save_contact_sheet)

        # 初始化 image_list 以避免 set_value 异常
        dpg.add_listbox(tag="image_list", items=[])

        with dpg.texture_registry():
            dpg.add_dynamic_texture(
                640, 640, [255] * 640 * 640 * 4, tag="contact_sheet_texture"
            )

        with dpg.drawlist(width=640, height=640, tag="contact_sheet_drawlist"):
            dpg.draw_image("contact_sheet_texture", [0, 0], [640, 640])

    dpg.create_viewport(title="Contact Sheet Creator", width=800, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
