# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.

import json  # 导入json模块，用于处理JSON数据
import pandas as pd  # 导入pandas库，用于数据处理
import dearpygui.dearpygui as dpg  # 导入Dear PyGui库，用于创建图形用户界面
import sys
import os
import platform  # 导入platform模块，用于检测操作系统
import subprocess


class JsonEditorFunctions:  # 定义JsonEditorFunctions类
    def __init__(self, dpg_instance):  # 初始化函数
        self.df = None  # 数据框
        self.file_path = ""  # 文件路径
        self.dpg = dpg_instance  # Dear PyGui实例
        self.column_types = {}  # 列类型字典

    def open_json(self, file_path):  # 打开JSON文件函数
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:  # 打开JSON文件
                    data = json.load(file)  # 读取JSON数据
                self.df = pd.json_normalize(data)  # 规范化JSON数据为数据框
                self.file_path = file_path  # 设置文件路径
                self.update_table()  # 更新表格
                self.dpg.configure_item(
                    self.save_menu_item, enabled=True
                )  # 启用保存菜单项
                self.show_message("File opened successfully")  # 显示文件打开成功消息
            except Exception as e:
                self.show_message(
                    f"Failed to open JSON file: {e}"
                )  # 显示文件打开失败消息

    def save_json(self):  # 保存JSON文件函数
        if self.df is not None:
            try:
                edited_data = self.df.to_dict(orient="records")  # 将数据框转换为字典
                with open(self.file_path, "w", encoding="utf-8") as file:  # 打开文件
                    json.dump(
                        edited_data, file, ensure_ascii=False, indent=4
                    )  # 写入JSON数据
                self.show_message(
                    f"Edited JSON data saved to {self.file_path}"
                )  # 显示文件保存成功消息
            except Exception as e:
                self.show_message(
                    f"Failed to save JSON file: {e}"
                )  # 显示文件保存失败消息

    def show_message(self, message):  # 显示消息函数
        self.dpg.set_value("message_text", message)  # 设置消息文本
        self.dpg.show_item("message_box")  # 显示消息框

    def edit_cell(self, sender, app_data, user_data):  # 编辑单元格函数
        index, col = user_data  # 获取行索引和列名
        if self.df is not None:
            if self.column_types.get(col) == "bool":  # 如果列类型是布尔值
                self.df.at[index, col] = app_data == "True"  # 设置单元格值
            else:
                self.df.at[index, col] = app_data  # 设置单元格值

    def add_row(self):  # 添加行函数
        if self.df is not None:
            new_row = {  # 创建新行
                col: self.get_default_value_for_type(self.column_types.get(col))
                for col in self.df.columns
            }
            self.df = pd.concat(
                [self.df, pd.DataFrame([new_row])], ignore_index=True
            )  # 添加新行到数据框
            self.update_table()  # 更新表格

    def add_column(self):  # 添加列函数
        self.dpg.show_item("column_dialog")  # 显示添加列对话框

    def add_column_name(self, sender, app_data):  # 添加列名函数
        new_col = self.dpg.get_value("new_column_name")  # 获取新列名
        new_col_type = self.dpg.get_value("new_column_type")  # 获取新列类型
        if new_col and self.df is not None:
            self.df[new_col] = self.get_default_value_for_type(
                new_col_type
            )  # 添加新列到数据框
            self.column_types[new_col] = new_col_type  # 设置新列类型
            self.update_table()  # 更新表格
        self.dpg.hide_item("column_dialog")  # 隐藏添加列对话框

    def delete_row(self):  # 删除行函数
        self.dpg.show_item("row_dialog")  # 显示删除行对话框

    def delete_row_by_index(self, sender, app_data):  # 根据索引删除行函数
        row_index = self.dpg.get_value("row_index")  # 获取行索引
        if row_index is not None and self.df is not None:
            if 0 <= row_index < len(self.df):
                self.df = self.df.drop(row_index).reset_index(drop=True)  # 删除行
                self.update_table()  # 更新表格
        self.dpg.hide_item("row_dialog")  # 隐藏删除行对话框

    def delete_column(self):  # 删除列函数
        self.dpg.show_item("column_delete_dialog")  # 显示删除列对话框

    def delete_column_by_name(self, sender, app_data):  # 根据列名删除列函数
        col_name = self.dpg.get_value("column_name_delete")  # 获取列名
        if col_name and self.df is not None:
            self.df = self.df.drop(columns=[col_name])  # 删除列
            if col_name in self.column_types:
                del self.column_types[col_name]  # 删除列类型
            self.update_table()  # 更新表格
        self.dpg.hide_item("column_delete_dialog")  # 隐藏删除列对话框

    def edit_column_name(self, sender, app_data):  # 编辑列名函数
        current_name = self.dpg.get_value("current_column_name")  # 获取当前列名
        new_name = self.dpg.get_value("new_column_name_edit")  # 获取新列名
        if self.df is not None and current_name in self.df.columns and new_name:
            self.df.rename(columns={current_name: new_name}, inplace=True)  # 重命名列
            if current_name in self.column_types:
                self.column_types[new_name] = self.column_types.pop(
                    current_name
                )  # 更新列类型
            self.update_table()  # 更新表格
        self.dpg.hide_item("edit_column_dialog")  # 隐藏编辑列名对话框

    def change_column_type(self, sender, app_data, user_data):  # 改变列类型函数
        col = user_data  # 获取列名
        self.column_types[col] = app_data  # 设置列类型
        self.update_table()  # 更新表格

    def get_default_value_for_type(self, col_type):  # 获取列类型的默认值函数
        if col_type == "int":
            return 0  # 返回整数默认值
        elif col_type == "float":
            return 0.0  # 返回浮点数默认值
        elif col_type == "bool":
            return False  # 返回布尔值默认值
        else:
            return ""  # 返回字符串默认值

    def set_file_association(self):  # 设置文件关联函数
        if platform.system() == "Windows":  # 如果是Windows系统
            try:
                exe_path = os.path.abspath(sys.argv[0])  # 获取可执行文件路径
                reg_content = f"""
                Windows Registry Editor Version 5.00

                [HKEY_CLASSES_ROOT\\.json]
                @="JsonEditorFile"

                [HKEY_CLASSES_ROOT\\JsonEditorFile]
                @="JSON File"
                "Content Type"="application/json"

                [HKEY_CLASSES_ROOT\\JsonEditorFile\\shell\\open\\command]
                @="\\"{exe_path}\\" \\"%1\\""
                """  # 注册表内容

                with open("file_association.reg", "w") as reg_file:  # 创建注册表文件
                    reg_file.write(reg_content)  # 写入注册表内容

                subprocess.run(
                    ["reg", "import", "file_association.reg"], check=True
                )  # 导入注册表文件
                os.remove("file_association.reg")  # 删除注册表文件
            except Exception as e:
                self.show_message(
                    f"Failed to set file association: {e}"
                )  # 显示设置文件关联失败的消息

    def remove_file_association(self):  # 移除文件关联函数
        if platform.system() == "Windows":  # 如果是Windows系统
            try:
                reg_content = """
                Windows Registry Editor Version 5.00

                [-HKEY_CLASSES_ROOT\\.json]
                [-HKEY_CLASSES_ROOT\\JsonEditorFile]
                """  # 注册表内容

                with open(
                    "remove_file_association.reg", "w"
                ) as reg_file:  # 创建注册表文件
                    reg_file.write(reg_content)  # 写入注册表内容

                subprocess.run(
                    ["reg", "import", "remove_file_association.reg"], check=True
                )  # 导入注册表文件
                os.remove("remove_file_association.reg")  # 删除注册表文件
            except Exception as e:
                self.show_message(
                    f"Failed to remove file association: {e}"
                )  # 显示移除文件关联失败的消息
