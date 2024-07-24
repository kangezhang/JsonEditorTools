# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.

import json
import pandas as pd
import dearpygui.dearpygui as dpg

class JsonEditorFunctions:
    def __init__(self, dpg_instance):
        self.df = None
        self.file_path = ""
        self.dpg = dpg_instance
        self.column_types = {}

    def open_json(self, file_path):
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                self.df = pd.json_normalize(data)
                self.file_path = file_path
                self.update_table()
                self.dpg.configure_item(self.save_menu_item, enabled=True)
                self.show_message("File opened successfully")
            except Exception as e:
                self.show_message(f"Failed to open JSON file: {e}")

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
        self.dpg.set_value("message_text", message)
        self.dpg.show_item("message_box")

    def edit_cell(self, sender, app_data, user_data):
        index, col = user_data
        if self.df is not None:
            if self.column_types.get(col) == "bool":
                self.df.at[index, col] = app_data == "True"
            else:
                self.df.at[index, col] = app_data

    def add_row(self):
        if self.df is not None:
            new_row = {
                col: self.get_default_value_for_type(self.column_types.get(col))
                for col in self.df.columns
            }
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.update_table()

    def add_column(self):
        self.dpg.show_item("column_dialog")

    def add_column_name(self, sender, app_data):
        new_col = self.dpg.get_value("new_column_name")
        new_col_type = self.dpg.get_value("new_column_type")
        if new_col and self.df is not None:
            self.df[new_col] = self.get_default_value_for_type(new_col_type)
            self.column_types[new_col] = new_col_type
            self.update_table()
        self.dpg.hide_item("column_dialog")

    def delete_row(self):
        self.dpg.show_item("row_dialog")

    def delete_row_by_index(self, sender, app_data):
        row_index = self.dpg.get_value("row_index")
        if row_index is not None and self.df is not None:
            if 0 <= row_index < len(self.df):
                self.df = self.df.drop(row_index).reset_index(drop=True)
                self.update_table()
        self.dpg.hide_item("row_dialog")

    def delete_column(self):
        self.dpg.show_item("column_delete_dialog")

    def delete_column_by_name(self, sender, app_data):
        col_name = self.dpg.get_value("column_name_delete")
        if col_name and self.df is not None:
            self.df = self.df.drop(columns=[col_name])
            if col_name in self.column_types:
                del self.column_types[col_name]
            self.update_table()
        self.dpg.hide_item("column_delete_dialog")

    def edit_column_name(self, sender, app_data):
        current_name = self.dpg.get_value("current_column_name")
        new_name = self.dpg.get_value("new_column_name_edit")
        if self.df is not None and current_name in self.df.columns and new_name:
            self.df.rename(columns={current_name: new_name}, inplace=True)
            if current_name in self.column_types:
                self.column_types[new_name] = self.column_types.pop(current_name)
            self.update_table()
        self.dpg.hide_item("edit_column_dialog")

    def change_column_type(self, sender, app_data, user_data):
        col = user_data
        self.column_types[col] = app_data
        self.update_table()

    def get_default_value_for_type(self, col_type):
        if col_type == "int":
            return 0
        elif col_type == "float":
            return 0.0
        elif col_type == "bool":
            return False
        else:
            return ""
