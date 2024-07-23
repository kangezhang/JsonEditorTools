import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import dearpygui.dearpygui as dpg
import platform

class JsonEditorApp:
    def __init__(self):
        self.df = None
        self.file_path = ""
        self.column_width = 150  # 每列的固定宽度

        dpg.create_context()

        # 初始化视口
        dpg.create_viewport(title="JSON Editor", width=1024, height=640, resizable=False)

        # 检测操作系统并设置字体路径
        font_path = self.get_font_path()

        # 注册字体
        with dpg.font_registry():
            default_font = dpg.add_font(font_path, 20)

        # 主窗口
        with dpg.window(label="", no_title_bar=True, no_resize=True, no_move=True, no_collapse=True, tag="Main Window"):
            self.create_menu()
            self.create_table_window()

        # 创建对话框
        self.create_dialogs()

        # 绑定字体
        dpg.bind_font(default_font)

        # 设置 Dear PyGui
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # 设置窗口大小变化的回调函数
        dpg.set_viewport_resize_callback(self.resize_callback)

    def get_font_path(self):
        if platform.system() == "Windows":
            return "C:/Windows/Fonts/Arial.ttf"
        elif platform.system() == "Darwin":  # macOS
            return "/System/Library/Fonts/Supplemental/Arial.ttf"
        else:
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 默认字体路径

    def create_menu(self):
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open JSON", callback=self.open_json)
                self.save_menu_item = dpg.add_menu_item(
                    label="Save JSON", callback=self.save_json, enabled=False
                )


            with dpg.menu(label="Edit"):
                dpg.add_menu_item(label="Add Row", callback=self.add_row)
                dpg.add_menu_item(label="Add Column", callback=self.add_column)
                dpg.add_menu_item(label="Delete Row", callback=self.delete_row)
                dpg.add_menu_item(label="Delete Column", callback=self.delete_column)

    def create_table_window(self):
        # 外部子窗口，启用水平滚动条
        with dpg.child_window(width=-1, height=-1, horizontal_scrollbar=True):
            # 内部子窗口，用于放置表格
            with dpg.child_window(width=1024, height=600, horizontal_scrollbar=True, tag="Table Window"):
                self.table_id = dpg.add_table(
                    header_row=True,
                    resizable=False,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    policy=dpg.mvTable_SizingFixedFit  # 确保列宽固定
                )

    def create_dialogs(self):
        # 添加列对话框
        with dpg.window(label="AddColumn", show=False, tag="column_dialog"):
            dpg.add_input_text(label="Column Name", tag="new_column_name")
            dpg.add_button(label="Add", callback=self.add_column_name)

        # 删除行对话框
        with dpg.window(label="Delete Row", show=False, tag="row_dialog"):
            dpg.add_input_int(label="Row Index", tag="row_index")
            dpg.add_button(label="Delete", callback=self.delete_row_by_index)

        # 删除列对话框
        with dpg.window(label="Delete Column", show=False, tag="column_delete_dialog"):
            dpg.add_input_text(label="Column Name", tag="column_name_delete")
            dpg.add_button(label="Delete", callback=self.delete_column_by_name)

        # 修改列名对话框
        with dpg.window(label="Edit Column Name", show=False, tag="edit_column_dialog"):
            dpg.add_input_text(label="Current Column Name", tag="current_column_name")
            dpg.add_input_text(label="New Column Name", tag="new_column_name_edit")
            dpg.add_button(label="Rename", callback=self.edit_column_name)

    def resize_callback(self, sender, app_data):
        width, height = dpg.get_viewport_client_width(), dpg.get_viewport_client_height()
        dpg.set_item_width("Main Window", width)
        dpg.set_item_height("Main Window", height)
        dpg.set_item_width("Table Window", width - 20)  # 留出一点空间以便水平滚动条
        dpg.set_item_height("Table Window", height - 100)  # 留出一些高度以便菜单和滚动条

    def open_json(self):
        file_path = self.open_file_dialog()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                self.df = pd.json_normalize(data)
                self.file_path = file_path
                self.update_table()
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
        if self.df is None:
            return

        columns = list(self.df.columns)
        total_width = len(columns) * self.column_width

        dpg.set_item_width("Table Window", total_width)  # 设置子窗口宽度

        # 添加行列索引
        dpg.add_table_column(label="", parent=self.table_id, width=self.column_width // 2)
        for col in columns:
            dpg.add_table_column(label=col, parent=self.table_id, width=self.column_width)

        with dpg.table_row(parent=self.table_id):
            dpg.add_text("", color=[178, 178, 178, 255])  # 空单元格
            for col_index, col in enumerate(columns):
                dpg.add_text(str(col_index), color=[178, 178, 178, 255])

        for index, row in self.df.iterrows():
            with dpg.table_row(parent=self.table_id):
                dpg.add_text(str(index), color=[178, 178, 178, 255])
                for col in columns:
                    dpg.add_input_text(
                        default_value=str(row[col]),
                        callback=self.edit_cell,
                        user_data=(index, col),
                        width=self.column_width  # 设置每个输入框的宽度
                    )

        # 强制刷新 UI
        dpg.configure_item(self.table_id, show=False)
        dpg.configure_item(self.table_id, show=True)

    def edit_cell(self, sender, app_data, user_data):
        index, col = user_data
        if self.df is not None:
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

    def delete_row(self):
        dpg.show_item("row_dialog")

    def delete_row_by_index(self, sender, app_data):
        row_index = dpg.get_value("row_index")
        if row_index is not None and self.df is not None:
            if 0 <= row_index < len(self.df):
                self.df = self.df.drop(row_index).reset_index(drop=True)
                self.update_table()
        dpg.hide_item("row_dialog")

    def delete_column(self):
        dpg.show_item("column_delete_dialog")

    def delete_column_by_name(self, sender, app_data):
        col_name = dpg.get_value("column_name_delete")
        if col_name and self.df is not None:
            self.df = self.df.drop(columns=[col_name])
            self.update_table()
        dpg.hide_item("column_delete_dialog")

    def edit_column_name(self, sender, app_data):
        current_name = dpg.get_value("current_column_name")
        new_name = dpg.get_value("new_column_name_edit")
        if self.df is not None and current_name in self.df.columns and new_name:
            self.df.rename(columns={current_name: new_name}, inplace=True)
            self.update_table()
        dpg.hide_item("edit_column_dialog")

    def save_json(self):
        if self.df is not None:
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
