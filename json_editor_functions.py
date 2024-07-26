# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.

import json  # 导入json模块，用于处理JSON数据
import pandas as pd  # 导入pandas库，用于数据处理
import sys
import os
import platform  # 导入platform模块，用于检测操作系统
import subprocess
import dearpygui.dearpygui as dpg  # 导入Dear PyGui库，用于创建图形用户界面


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
            if self.index_color_differentiation:
                new_row["ColorDif"] = "#000000"  # 默认颜色
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

    def resize_callback(self, sender, app_data):  # 视口大小调整回调函数
        width, height = (
            dpg.get_viewport_client_width(),
            dpg.get_viewport_client_height(),
        )  # 获取视口宽度和高度
        dpg.set_item_width("Main Window", width)  # 设置主窗口宽度
        dpg.set_item_height("Main Window", height)  # 设置主窗口高度
        dpg.set_item_width("Table Window", width - 20)  # 设置表格窗口宽度
        dpg.set_item_height("Table Window", height - 60)  # 设置表格窗口高度

    def show_add_row_dialog(self):  # 显示添加行对话框函数
        dpg.show_item("row_dialog")  # 显示对话框
        dpg.focus_item("row_dialog")  # 使对话框获得焦点

    def show_add_column_dialog(self):  # 显示添加列对话框函数
        dpg.configure_item("column_dialog")
        dpg.set_item_width("column_dialog", 420)
        dpg.set_item_height("column_dialog", 240)
        dpg.show_item("column_dialog")  # 显示对话框
        dpg.focus_item("column_dialog")  # 使对话框获得焦点

    def show_delete_row_dialog(self):  # 显示删除行对话框函数
        dpg.configure_item("delete_row_dialog")
        dpg.set_item_width("delete_row_dialog", 420)
        dpg.set_item_height("delete_row_dialog", 240)
        dpg.show_item("delete_row_dialog")  # 使用匹配的标签
        dpg.focus_item("delete_row_dialog")  # 使对话框获得焦点

    def show_delete_column_dialog(self):  # 显示删除列对话框函数
        dpg.configure_item("column_delete_dialog")
        dpg.set_item_width("column_delete_dialog", 420)
        dpg.set_item_height("column_delete_dialog", 240)
        dpg.show_item("column_delete_dialog")  # 显示对话框
        dpg.focus_item("column_delete_dialog")  # 使对话框获得焦点

    def show_open_file_dialog(self):  # 显示打开文件对话框函数

        dpg.set_item_width("file_dialog_id", 680)
        dpg.set_item_height("file_dialog_id", 420)
        dpg.show_item("file_dialog_id")  # 显示对话框
        dpg.focus_item("file_dialog_id")  # 使对话框获得焦点

    def toggle_index_color_differentiation(self, sender, app_data, user_data):
        self.index_color_differentiation = app_data  # 获取索引颜色区分的值

    def show_settings_dialog(self):  # 显示设置对话框函数
        # dpg.hide_item("file_dialog_id")
        dpg.configure_item("settings_dialog")
        dpg.set_item_width("settings_dialog", 420)
        dpg.set_item_height("settings_dialog", 240)
        dpg.show_item("settings_dialog")  # 显示对话框
        dpg.focus_item("settings_dialog")  # 使对话框获得焦点

    def show_import_excel_dialog(self):  # 显示导入Excel列对话框函数
        dpg.configure_item("import_excel_dialog")
        dpg.set_item_width("import_excel_dialog", 420)
        dpg.set_item_height("import_excel_dialog", 300)
        dpg.show_item("import_excel_dialog")  # 显示对话框
        dpg.focus_item("import_excel_dialog")  # 使对话框获得焦点

    def show_select_excel_file_dialog(self):  # 显示选择Excel文件对话框函数
        dpg.show_item("select_excel_file_dialog")  # 显示对话框
        dpg.focus_item("select_excel_file_dialog")  # 使对话框获得焦点

    def open_file_callback(self, sender, app_data):  # 打开文件回调函数
        self.open_json(app_data["file_path_name"])  # 打开JSON文件

    def select_excel_file_callback(self, sender, app_data):  # 选择Excel文件回调函数
        excel_file_path = app_data["file_path_name"]  # 获取Excel文件路径
        dpg.set_value("excel_file_path", excel_file_path)  # 设置Excel文件路径
        self.update_sheet_names(excel_file_path)  # 更新工作表名

    def update_sheet_names(self, excel_file_path):  # 更新工作表名函数
        try:
            sheet_names = pd.ExcelFile(excel_file_path).sheet_names  # 获取工作表名
            dpg.configure_item("sheet_name", items=sheet_names)  # 配置工作表名下拉框
        except Exception as e:
            self.show_message(
                f"Failed to read sheet names: {e}"
            )  # 显示读取工作表名失败的消息

    def apply_settings(self):  # 应用设置函数
        is_enabled = dpg.get_value(
            "index_color_differentiation_checkbox"
        )  # 获取启用索引颜色区分复选框的值
        self.index_color_differentiation = is_enabled  # 设置类属性

        # 更新表格以应用新设置
        self.update_table()

        # 显示设置已应用的消息
        self.show_message(
            f"Settings applied. Index color differentiation enabled: {is_enabled}"
        )  # 显示设置已应用的消息

    def import_excel_column(self):  # 导入Excel列函数
        excel_file_path = dpg.get_value("excel_file_path")  # 获取Excel文件路径
        sheet_name = dpg.get_value("sheet_name")  # 获取工作表名
        excel_column = dpg.get_value("excel_column")  # 获取Excel列名
        target_json_column = dpg.get_value("target_json_column")  # 获取目标JSON列名

        try:
            excel_data = pd.read_excel(
                excel_file_path, sheet_name=sheet_name, usecols=[excel_column]
            )  # 读取Excel数据
            if target_json_column not in self.df.columns:  # 如果目标JSON列不存在
                self.df[target_json_column] = ""  # 添加目标JSON列

            if len(excel_data) > len(self.df):  # 如果Excel数据行数大于JSON数据行数
                for _ in range(len(excel_data) - len(self.df)):
                    self.add_row()  # 添加行

            self.df[target_json_column] = excel_data[
                excel_column
            ].values  # 将Excel列数据导入目标JSON列
            self.update_table()  # 更新表格
            self.show_message(
                "Excel column imported successfully"
            )  # 显示导入成功的消息
        except Exception as e:
            self.show_message(
                f"Failed to import Excel column: {e}"
            )  # 显示导入失败的消息

    def change_language(self, sender, app_data):  # 切换语言函数
        selected_language = (
            "English" if app_data == self.texts["English"]["english"] else "Chinese"
        )  # 根据选择的语言设置语言变量
        self.language = selected_language  # 更新语言
        self.refresh_ui_texts()  # 刷新UI文本

    def refresh_ui_texts(self):
        # 更新窗口和菜单栏的标签
        dpg.set_item_label("Main Window", self.texts[self.language]["main_window"])
        # dpg.set_item_label(self.open_menu_item, self.texts[self.language]["open_json"])
        dpg.set_item_label(self.save_menu_item, self.texts[self.language]["save_json"])
        dpg.set_item_label(
            self.setting_menu_item, self.texts[self.language]["settings"]
        )

        # 更新菜单标签
        menu_items = {
            "file_menu": self.texts[self.language]["file_menu"],
            "edit_menu": self.texts[self.language]["edit_menu"],
            "editor_menu": self.texts[self.language]["editor_menu"],
        }

        for item_tag, label in menu_items.items():
            dpg.set_item_label(item_tag, label)

        # 更新对话框和按钮标签
        dialog_items = {
            "column_dialog": [
                ("column_name", "new_column_name"),
                ("column_type", "new_column_type"),
                ("add", "add"),
                ("close", "close"),
            ],
            "row_dialog": [
                ("row_index", "row_index"),
                ("add", "add"),
                ("close", "close"),
            ],
            "row_delete_dialog": [
                ("row_index", "row_index"),
                ("delete", "delete"),
                ("close", "close"),
            ],
            "column_delete_dialog": [
                ("delete_column_name", "column_name_delete"),
                ("delete", "delete"),
                ("close", "close"),
            ],
            "edit_column_dialog": [
                ("current_column_name", "current_column_name"),
                ("new_column_name", "new_column_name_edit"),
                ("rename", "rename"),
                ("close", "close"),
            ],
            "message_box": [("close", "close")],
            "settings_dialog": [
                ("enable_feature", "enable_feature_checkbox"),
                ("apply", "apply"),
                ("language", "language_combo"),
                ("close", "close"),
            ],
            "import_excel_dialog": [
                ("select_excel_file", "select_excel_file"),
                ("selected_excel_file", "excel_file_path"),
                ("sheet_name", "sheet_name"),
                ("excel_column", "excel_column"),
                ("target_json_column", "target_json_column"),
                ("import", "import"),
                ("close", "close"),
            ],
        }

        for dialog_tag, items in dialog_items.items():
            for label, tag in items:
                dpg.set_item_label(tag, self.texts[self.language][label])

    def get_font_path(self):  # 获取字体路径函数
        if platform.system() == "Windows":  # 如果是Windows系统
            return "C:/Windows/Fonts/simhei.ttf"  # 返回SimHei字体路径
        elif platform.system() == "Darwin":  # 如果是macOS系统
            return "/System/Library/Fonts/Supplemental/Arial.ttf"  # 返回Arial字体路径
        else:  # 如果是Linux系统
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 返回DejaVuSans字体路径

    def show_color_picker(self, sender, app_data, user_data):  # 显示颜色选择器函数
        index, col = user_data
        with dpg.window(
            label="Color Picker",
            modal=True,
            tag="color_picker_window",
            width=400,
            height=400,
        ):
            dpg.add_color_picker(
                callback=self.color_picker_callback, user_data=(index, col)
            )
            dpg.add_button(
                label="Close", callback=lambda: dpg.delete_item("color_picker_window")
            )

    def color_picker_callback(self, sender, app_data, user_data):  # 颜色选择器回调函数
        index, col = user_data
        color = "#{:02x}{:02x}{:02x}".format(
            int(app_data[0] * 255), int(app_data[1] * 255), int(app_data[2] * 255)
        )
        self.df.at[index, col] = color
        self.update_table()

    def create_dialogs(self):  # 创建对话框函数
        with dpg.window(
            label=self.texts[self.language]["add_column_dialog"],
            show=False,
            tag="column_dialog",
        ):  # 创建添加列对话框
            dpg.add_input_text(
                label=self.texts[self.language]["column_name"], tag="new_column_name"
            )  # 添加输入框，用于输入列名
            dpg.add_combo(
                label=self.texts[self.language]["column_type"],
                items=["string", "int", "float", "bool"],
                tag="new_column_type",
            )  # 添加下拉框，用于选择列类型
            dpg.add_button(
                label=self.texts[self.language]["add"],
                callback=self.add_column_name,
                tag="add_column_button",
            )  # 添加按钮，用于添加列
            dpg.add_same_line()
            dpg.add_button(
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("column_dialog"),
                tag="close_column_dialog_button",
            )  # 添加关闭按钮

            # 删除行对话框
            with dpg.window(
                label=self.texts[self.language]["delete_row"],
                show=False,
                tag="delete_row_dialog",  # 更正这个标签
            ):
                dpg.add_input_int(
                    label=self.texts[self.language]["row_index"], tag="row_index"
                )  # 添加输入框，用于输入行索引
                dpg.add_button(
                    label=self.texts[self.language]["delete"],
                    callback=self.delete_row_by_index,  # 确保回调函数是正确的
                    tag="delete_row_button",
                )  # 添加按钮，用于删除行

            with dpg.window(
                label=self.texts[self.language]["delete_column_dialog"],
                show=False,
                tag="column_delete_dialog",
            ):  # 创建删除列对话框
                dpg.add_input_text(
                    label=self.texts[self.language]["delete_column_name"],
                    tag="column_name_delete",
                )  # 添加输入框，用于输入列名
                dpg.add_button(
                    label=self.texts[self.language]["delete"],
                    callback=self.delete_column_by_name,
                    tag="delete_column_button",
                )  # 添加按钮，用于删除列
                dpg.add_same_line()
                dpg.add_button(
                    label=self.texts[self.language]["close"],
                    callback=lambda: dpg.hide_item("column_delete_dialog"),
                    tag="close_column_delete_dialog_button",
                )  # 添加关闭按钮

            with dpg.window(
                label=self.texts[self.language]["edit_column_dialog"],
                show=False,
                modal=True,
                tag="edit_column_dialog",
            ):  # 创建编辑列名对话框
                dpg.add_input_text(
                    label=self.texts[self.language]["current_column_name"],
                    tag="current_column_name",
                )  # 添加输入框，用于输入当前列名
                dpg.add_input_text(
                    label=self.texts[self.language]["new_column_name"],
                    tag="new_column_name_edit",
                )  # 添加输入框，用于输入新列名
                dpg.add_button(
                    label=self.texts[self.language]["rename"],
                    callback=self.edit_column_name,
                    tag="rename_column_button",
                )  # 添加按钮，用于重命名列
                dpg.add_same_line()
                dpg.add_button(
                    label=self.texts[self.language]["close"],
                    callback=lambda: dpg.hide_item("edit_column_dialog"),
                    tag="close_edit_column_dialog_button",
                )  # 添加关闭按钮

            with dpg.window(
                label=self.texts[self.language]["message_box"],
                show=False,
                tag="message_box",
            ):  # 创建消息框
                dpg.add_text("", tag="message_text")  # 添加文本标签
                dpg.add_button(
                    label=self.texts[self.language]["close"],
                    callback=lambda: dpg.hide_item("message_box"),
                    tag="close_message_box_button",
                )  # 添加关闭按钮

            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=self.open_file_callback,
                tag="file_dialog_id",
            ):  # 创建文件对话框
                dpg.add_file_extension(
                    ".json", color=(150, 255, 150, 255)
                )  # 添加文件扩展名过滤器

            with dpg.window(
                label=self.texts[self.language]["settings_dialog"],
                show=False,
                modal=True,  # 模态窗口可以让用户在关闭对话框之前无法与其他窗口交互
                tag="settings_dialog",
            ):  # 创建设置对话框
                dpg.add_checkbox(
                    label=self.texts[self.language]["enable_feature"],
                    tag="enable_feature_checkbox",
                )  # 添加复选框，用于启用功能

                dpg.add_checkbox(
                    label="Enable Index Color Differentiation",
                    default_value=self.index_color_differentiation,
                    callback=self.toggle_index_color_differentiation,
                    tag="index_color_differentiation_checkbox",
                )  #

                dpg.add_combo(
                    label=self.texts[self.language]["language"],
                    items=[
                        self.texts["English"]["english"],
                        self.texts["Chinese"]["chinese"],
                    ],
                    tag="language_combo",
                    default_value=self.texts[self.language]["english"],
                    callback=self.change_language,
                )  # 添加下拉框，用于选择语言
                dpg.add_button(
                    label=self.texts[self.language]["apply"],
                    callback=self.apply_settings,
                    tag="apply_settings_button",
                )  # 添加按钮，用于应用设置
                dpg.add_same_line()

            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=self.select_excel_file_callback,
                tag="select_excel_file_dialog",
            ):  # 创建选择Excel文件对话框
                dpg.add_file_extension(
                    ".xlsx", color=(150, 255, 150, 255)
                )  # 添加xlsx文件扩展名过滤器
                dpg.add_file_extension(
                    ".xls", color=(150, 255, 150, 255)
                )  # 添加xls文件扩展名过滤器

            with dpg.window(
                label=self.texts[self.language]["import_excel_dialog"],
                show=False,
                modal=False,
                tag="import_excel_dialog",
            ):  # 创建导入Excel列对话框
                dpg.add_button(
                    label=self.texts[self.language]["select_excel_file"],
                    callback=self.show_select_excel_file_dialog,
                    tag="select_excel_file_button",
                )  # 添加按钮，用于选择Excel文件
                dpg.add_input_text(
                    label=self.texts[self.language]["selected_excel_file"],
                    tag="excel_file_path",
                    readonly=True,
                )  # 添加输入框，用于显示选择的Excel文件路径
                dpg.add_combo(
                    label=self.texts[self.language]["sheet_name"],
                    tag="sheet_name",
                    items=[],
                )  # 添加下拉框，用于选择工作表名
                dpg.add_input_text(
                    label=self.texts[self.language]["excel_column"], tag="excel_column"
                )  # 添加输入框，用于输入Excel列名
                dpg.add_input_text(
                    label=self.texts[self.language]["target_json_column"],
                    tag="target_json_column",
                )  # 添加输入框，用于输入目标JSON列名
                dpg.add_button(
                    label=self.texts[self.language]["import"],
                    callback=self.import_excel_column,
                    tag="import_excel_column_button",
                )  # 添加按钮，用于导入Excel列
                dpg.add_same_line()
                dpg.add_button(
                    label=self.texts[self.language]["close"],
                    callback=lambda: dpg.hide_item("import_excel_dialog"),
                    tag="close_import_excel_dialog_button",
                )  # 添加关闭按钮

    languageDirc = {  # 定义中英文文本字典
        "English": {  # 英文文本
            "main_window": "Main Window",
            "file_menu": "File",
            "open_json": "Open JSON",
            "save_json": "Save JSON",
            "edit_menu": "Edit",
            "add_row": "Add Row",
            "add_column": "Add Column",
            "delete_row": "Delete Row",
            "delete_column": "Delete Column",
            "import_excel_column": "Import Excel Column",
            "editor_menu": "Editor",
            "settings": "Settings",
            "add_column_dialog": "Add Column",
            "column_name": "Column Name",
            "column_type": "Column Type",
            "add": "Add",
            "close": "Close",
            "delete_row_dialog": "Delete Row",
            "row_index": "Row Index",
            "delete": "Delete",
            "delete_column_dialog": "Delete Column",
            "delete_column_name": "Column Name",
            "edit_column_dialog": "Edit Column Name",
            "current_column_name": "Current Column Name",
            "new_column_name": "New Column Name",
            "rename": "Rename",
            "message_box": "Message Box",
            "settings_dialog": "Settings",
            "enable_feature": "Enable Feature",
            "apply": "Apply",
            "import_excel_dialog": "Import Excel Column",
            "select_excel_file": "Select Excel File",
            "selected_excel_file": "Selected Excel File",
            "sheet_name": "Sheet Name",
            "excel_column": "Excel Column",
            "target_json_column": "Target JSON Column",
            "import": "Import",
            "language": "Language",
            "english": "English",
            "chinese": "Chinese",
        },
        "Chinese": {  # 中文文本
            "main_window": "主窗口",
            "file_menu": "文件",
            "open_json": "打开 JSON",
            "save_json": "保存 JSON",
            "edit_menu": "编辑",
            "add_row": "添加行",
            "add_column": "添加列",
            "delete_row": "删除行",
            "delete_column": "删除列",
            "import_excel_column": "导入 Excel 列",
            "editor_menu": "编辑器",
            "settings": "设置",
            "add_column_dialog": "添加列",
            "column_name": "列名",
            "column_type": "列类型",
            "add": "添加",
            "close": "关闭",
            "delete_row_dialog": "删除行",
            "row_index": "行索引",
            "delete": "删除",
            "delete_column_dialog": "删除列",
            "delete_column_name": "列名",
            "edit_column_dialog": "编辑列名",
            "current_column_name": "当前列名",
            "new_column_name": "新列名",
            "rename": "重命名",
            "message_box": "消息框",
            "settings_dialog": "设置",
            "enable_feature": "启用功能",
            "apply": "应用",
            "import_excel_dialog": "导入 Excel 列",
            "select_excel_file": "选择 Excel 文件",
            "selected_excel_file": "已选择的 Excel 文件",
            "sheet_name": "工作表名",
            "excel_column": "Excel 列",
            "target_json_column": "目标 JSON 列",
            "import": "导入",
            "language": "语言",
            "english": "英文",
            "chinese": "中文",
        },
    }
