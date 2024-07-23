import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import dearpygui.dearpygui as dpg


class JsonEditorApp:
    def __init__(self):
        self.df = None
        self.file_path = ""

        dpg.create_context()

        # 初始化视口
        dpg.create_viewport(title="JSON Editor", width=1024, height=640, resizable=True)

        # 注册字体
        with dpg.font_registry():
            default_font = dpg.add_font("C:/Windows/Fonts/Arial.ttf", 20)

        # 主窗口
        with dpg.window(
            label="",
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            tag="Main Window",
        ):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Open JSON", callback=self.open_json)
                    self.save_menu_item = dpg.add_menu_item(
                        label="Save JSON", callback=self.save_json, enabled=False
                    )
                    dpg.add_menu_item(
                        label="Exit", callback=lambda: dpg.destroy_context()
                    )

                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(label="Add Row", callback=self.add_row)
                    dpg.add_menu_item(label="Add Column", callback=self.add_column)

            with dpg.child_window(autosize_x=True, autosize_y=True, tag="Table Window"):
                self.table_id = dpg.add_table(
                    header_row=True,
                    resizable=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                )

        # 添加列对话框
        with dpg.window(label="Add Column", show=False, tag="column_dialog"):
            dpg.add_input_text(label="Column Name", tag="new_column_name")
            dpg.add_button(label="Add", callback=self.add_column_name)

        # 绑定字体
        dpg.bind_font(default_font)

        # 设置 Dear PyGui
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # 设置窗口大小变化的回调函数
        dpg.set_viewport_resize_callback(self.resize_callback)

    def resize_callback(self, sender, app_data):
        width, height = (
            dpg.get_viewport_client_width(),
            dpg.get_viewport_client_height(),
        )
        dpg.set_item_width("Main Window", width)
        dpg.set_item_height("Main Window", height)
        dpg.set_item_width("Table Window", width)
        dpg.set_item_height("Table Window", height)

    def open_json(self):
        file_path = self.open_file_dialog()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                self.df = pd.json_normalize(data)
                self.update_table()
                self.file_path = file_path
                dpg.configure_item(self.save_menu_item, enabled=True)
                self.show_message("File opened successfully")
            except Exception as e:
                self.show_message(f"Failed to open JSON file: {e}")

    def open_file_dialog(self):
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        return file_path

    def update_table(self):
        dpg.delete_item(self.table_id, children_only=True)
        columns = list(self.df.columns)
        for col in columns:
            dpg.add_table_column(label=col, parent=self.table_id)

        for index, row in self.df.iterrows():
            with dpg.table_row(parent=self.table_id):
                for col in columns:
                    dpg.add_input_text(
                        default_value=str(row[col]),
                        callback=self.edit_cell,
                        user_data=(index, col),
                    )

    def edit_cell(self, sender, app_data, user_data):
        index, col = user_data
        self.df.at[index, col] = app_data

    def add_row(self):
        if self.df is not None:
            new_row = {col: "" for col in self.df.columns}
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.update_table()

    def add_column(self):
        dpg.show_item("column_dialog")

    def add_column_name(self, sender, app_data):
        new_col = dpg.get_value("new_column_name")
        if new_col and self.df is not None:
            self.df[new_col] = ""
            self.update_table()
        dpg.hide_item("column_dialog")

    def save_json(self):
        try:
            edited_data = self.df.to_dict(orient="records")
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(edited_data, file, ensure_ascii=False, indent=4)
            self.show_message(f"Edited JSON data saved to {self.file_path}")
        except Exception as e:
            self.show_message(f"Failed to save JSON file: {e}")

    def show_message(self, message):
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Information", message)

    def run(self):
        dpg.start_dearpygui()
        dpg.destroy_context()


if __name__ == "__main__":
    app = JsonEditorApp()
    app.run()
