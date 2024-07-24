# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.
# -*- coding: utf-8 -*-

import dearpygui.dearpygui as dpg
import platform
from json_editor_functions import JsonEditorFunctions
import os
import subprocess
import sys

class JsonEditorApp(JsonEditorFunctions):
    def __init__(self):
        super().__init__(dpg)
        self.column_width = 150

        dpg.create_context()

        dpg.create_viewport(
            title="JSON Editor",
            width=1024,
            height=640,
            resizable=True,
            small_icon="1.ico",
            large_icon="1.ico",
        )

        FONT = self.get_font_path()
        with dpg.font_registry():
            with dpg.font(FONT, 20) as ft:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.bind_font(ft)

        with dpg.window(
            label="Main Window",
            no_title_bar=True,
            no_resize=True,
            no_move=True,
            no_collapse=True,
            tag="Main Window",
            width=-1,
            height=-1,
        ):
            self.create_menu()
            self.create_table_window()

        self.create_dialogs()

        dpg.setup_dearpygui()
        dpg.show_viewport()

        dpg.set_viewport_resize_callback(self.resize_callback)

    def get_font_path(self):
        if platform.system() == "Windows":
            return "C:/Windows/Fonts/simhei.ttf"
        elif platform.system() == "Darwin":
            return "/System/Library/Fonts/Supplemental/Arial.ttf"
        else:
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def create_menu(self):
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open JSON", callback=self.show_open_file_dialog)
                self.save_menu_item = dpg.add_menu_item(
                    label="Save JSON",
                    callback=self.save_json,
                    enabled=False,
                )

            with dpg.menu(label="Edit"):
                dpg.add_menu_item(label="Add Row", callback=self.add_row)
                dpg.add_menu_item(label="Add Column", callback=self.show_add_column_dialog)
                dpg.add_menu_item(label="Delete Row", callback=self.show_delete_row_dialog)
                dpg.add_menu_item(label="Delete Column", callback=self.show_delete_column_dialog)

            with dpg.menu(label="Editor"):
                dpg.add_menu_item(label="Settings", callback=self.show_settings_dialog)

    def create_table_window(self):
        with dpg.child_window(
            width=-1, height=-1, horizontal_scrollbar=True, tag="Table Window"
        ):
            self.table_id = dpg.add_table(
                header_row=True,
                resizable=False,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                policy=dpg.mvTable_SizingFixedFit,
            )

    def create_dialogs(self):
        with dpg.window(label="Add Column", show=False, tag="column_dialog"):
            dpg.add_input_text(label="Column Name", tag="new_column_name")
            dpg.add_combo(label="Column Type", items=["string", "int", "float", "bool"], tag="new_column_type")
            dpg.add_button(label="Add", callback=self.add_column_name)

        with dpg.window(label="Delete Row", show=False, tag="row_dialog"):
            dpg.add_input_int(label="Row Index", tag="row_index")
            dpg.add_button(label="Delete", callback=self.delete_row_by_index)

        with dpg.window(label="Delete Column", show=False, tag="column_delete_dialog"):
            dpg.add_input_text(label="Column Name", tag="column_name_delete")
            dpg.add_button(label="Delete", callback=self.delete_column_by_name)

        with dpg.window(label="Edit Column Name", show=False, tag="edit_column_dialog"):
            dpg.add_input_text(label="Current Column Name", tag="current_column_name")
            dpg.add_input_text(label="New Column Name", tag="new_column_name_edit")
            dpg.add_button(label="Rename", callback=self.edit_column_name)

        with dpg.window(label="Message Box", show=False, tag="message_box"):
            dpg.add_text("", tag="message_text")
            dpg.add_button(label="OK", callback=lambda: dpg.hide_item("message_box"))

        with dpg.file_dialog(directory_selector=False, show=False, callback=self.open_file_callback, tag="file_dialog_id"):
            dpg.add_file_extension(".json", color=(150, 255, 150, 255))

        with dpg.window(label="Settings", show=False, tag="settings_dialog"):
            dpg.add_checkbox(label="Enable Feature", tag="enable_feature_checkbox")
            dpg.add_button(label="Apply", callback=self.apply_settings)

    def resize_callback(self, sender, app_data):
        width, height = dpg.get_viewport_client_width(), dpg.get_viewport_client_height()
        dpg.set_item_width("Main Window", width)
        dpg.set_item_height("Main Window", height)
        dpg.set_item_width("Table Window", width - 20)
        dpg.set_item_height("Table Window", height - 60)

    def update_table(self):
        dpg.delete_item(self.table_id, children_only=True)
        if self.df is None:
            return

        columns = list(self.df.columns)
        total_width = len(columns) * self.column_width

        dpg.set_item_width(self.table_id, total_width)

        for col in columns:
            dpg.add_table_column(label=col, parent=self.table_id, width=self.column_width)

        with dpg.table_row(parent=self.table_id):
            for col in columns:
                dpg.add_combo(items=["string", "int", "float", "bool"], default_value=self.column_types.get(col, "string"), user_data=col, callback=self.change_column_type)

        for index, row in self.df.iterrows():
            with dpg.table_row(parent=self.table_id):
                for col in columns:
                    if self.column_types.get(col) == "bool":
                        dpg.add_combo(items=["True", "False"], default_value="True" if row[col] else "False", user_data=(index, col), callback=self.edit_cell, width=self.column_width)
                    else:
                        dpg.add_input_text(default_value=str(row[col]), callback=self.edit_cell, user_data=(index, col), width=self.column_width)

    def show_add_column_dialog(self):
        dpg.show_item("column_dialog")

    def show_delete_row_dialog(self):
        dpg.show_item("row_dialog")

    def show_delete_column_dialog(self):
        dpg.show_item("column_delete_dialog")

    def show_open_file_dialog(self):
        dpg.show_item("file_dialog_id")

    def open_file_callback(self, sender, app_data):
        self.open_json(app_data['file_path_name'])

    def show_settings_dialog(self):
        dpg.show_item("settings_dialog")

    def apply_settings(self):
        is_enabled = dpg.get_value("enable_feature_checkbox")
        if is_enabled:
            self.set_file_association()
        else:
            self.remove_file_association()
        dpg.hide_item("settings_dialog")
        self.show_message(f"Settings applied. Feature enabled: {is_enabled}")

    def set_file_association(self):
        if platform.system() == "Windows":
            try:
                exe_path = os.path.abspath(sys.argv[0])
                reg_content = f'''
                Windows Registry Editor Version 5.00

                [HKEY_CLASSES_ROOT\\.json]
                @="JsonEditorFile"

                [HKEY_CLASSES_ROOT\\JsonEditorFile]
                @="JSON File"
                "Content Type"="application/json"

                [HKEY_CLASSES_ROOT\\JsonEditorFile\\shell\\open\\command]
                @="\\"{exe_path}\\" \\"%1\\""
                '''

                with open("file_association.reg", "w") as reg_file:
                    reg_file.write(reg_content)

                subprocess.run(['reg', 'import', 'file_association.reg'], check=True)
                os.remove("file_association.reg")
            except Exception as e:
                self.show_message(f"Failed to set file association: {e}")

    def remove_file_association(self):
        if platform.system() == "Windows":
            try:
                reg_content = '''
                Windows Registry Editor Version 5.00

                [-HKEY_CLASSES_ROOT\\.json]
                [-HKEY_CLASSES_ROOT\\JsonEditorFile]
                '''

                with open("remove_file_association.reg", "w") as reg_file:
                    reg_file.write(reg_content)

                subprocess.run(['reg', 'import', 'remove_file_association.reg'], check=True)
                os.remove("remove_file_association.reg")
            except Exception as e:
                self.show_message(f"Failed to remove file association: {e}")

    def run(self):
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = JsonEditorApp()
    app.run()
