# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.
# -*- coding: utf-8 -*-

import dearpygui.dearpygui as dpg  # 导入Dear PyGui库，用于创建图形用户界面
import platform  # 导入platform模块，用于检测操作系统
from json_editor_functions import JsonEditorFunctions  # 导入JsonEditorFunctions类
import os
import subprocess
import sys
import pandas as pd  # 导入pandas库，用于数据处理


class JsonEditorApp(
    JsonEditorFunctions
):  # 定义JsonEditorApp类，继承自JsonEditorFunctions
    def __init__(self):  # 初始化函数
        super().__init__(dpg)  # 调用父类的初始化函数
        self.column_width = 150  # 每列的固定宽度
        self.language = "English"  # 默认语言为英语

        dpg.create_context()  # 创建Dear PyGui上下文

        dpg.create_viewport(  # 创建视口
            title="JSON Editor",  # 视口标题
            width=1024,  # 视口宽度
            height=640,  # 视口高度
            resizable=True,  # 视口可调整大小
            small_icon="1.ico",  # 小图标
            large_icon="1.ico",  # 大图标
        )

        FONT = self.get_font_path()  # 获取字体路径
        with dpg.font_registry():  # 注册字体
            with dpg.font(FONT, 20) as ft:  # 设置字体大小为20
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)  # 默认字体范围提示
                dpg.add_font_range_hint(
                    dpg.mvFontRangeHint_Chinese_Simplified_Common
                )  # 简体中文常用字体范围提示
                dpg.add_font_range_hint(
                    dpg.mvFontRangeHint_Chinese_Full
                )  # 全部简体中文字体范围提示
            dpg.bind_font(ft)  # 绑定字体

        self.texts = {  # 定义中英文文本字典
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

        with dpg.window(  # 创建主窗口
            label=self.texts[self.language]["main_window"],  # 主窗口标签
            no_title_bar=True,  # 无标题栏
            no_resize=True,  # 不可调整大小
            no_move=True,  # 不可移动
            no_collapse=True,  # 不可折叠
            tag="Main Window",  # 主窗口标签
            width=-1,  # 宽度
            height=-1,  # 高度
        ):
            self.create_menu()  # 创建菜单
            self.create_table_window()  # 创建表格窗口

        self.create_dialogs()  # 创建对话框

        dpg.setup_dearpygui()  # 设置Dear PyGui
        dpg.show_viewport()  # 显示视口

        dpg.set_viewport_resize_callback(
            self.resize_callback
        )  # 设置视口大小调整回调函数

    def get_font_path(self):  # 获取字体路径函数
        if platform.system() == "Windows":  # 如果是Windows系统
            return "C:/Windows/Fonts/simhei.ttf"  # 返回SimHei字体路径
        elif platform.system() == "Darwin":  # 如果是macOS系统
            return "/System/Library/Fonts/Supplemental/Arial.ttf"  # 返回Arial字体路径
        else:  # 如果是Linux系统
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 返回DejaVuSans字体路径

    def create_menu(self):  # 创建菜单函数
        with dpg.menu_bar():  # 创建菜单栏
            with dpg.menu(
                label=self.texts[self.language]["file_menu"], tag="file_menu"
            ):  # 创建文件菜单
                dpg.add_menu_item(
                    label=self.texts[self.language]["open_json"],
                    callback=self.show_open_file_dialog,
                    tag="open_json_menu_item",
                )  # 添加打开JSON菜单项
                self.save_menu_item = dpg.add_menu_item(  # 添加保存JSON菜单项
                    label=self.texts[self.language]["save_json"],  # 菜单项标签
                    callback=self.save_json,  # 回调函数
                    enabled=False,  # 默认禁用
                    tag="save_json_menu_item",  # 菜单项标签
                )

            with dpg.menu(
                label=self.texts[self.language]["edit_menu"], tag="edit_menu"
            ):  # 创建编辑菜单
                dpg.add_menu_item(
                    label=self.texts[self.language]["add_row"],
                    callback=self.show_add_row_dialog,
                    tag="add_row_menu_item",
                )  # 添加添加行菜单项
                dpg.add_menu_item(
                    label=self.texts[self.language]["add_column"],
                    callback=self.show_add_column_dialog,
                    tag="add_column_menu_item",
                )  # 添加添加列菜单项
                dpg.add_menu_item(
                    label=self.texts[self.language]["delete_row"],
                    callback=self.show_delete_row_dialog,
                    tag="delete_row_menu_item",
                )  # 添加删除行菜单项
                dpg.add_menu_item(
                    label=self.texts[self.language]["delete_column"],
                    callback=self.show_delete_column_dialog,
                    tag="delete_column_menu_item",
                )  # 添加删除列菜单项
                dpg.add_menu_item(
                    label=self.texts[self.language]["import_excel_column"],
                    callback=self.show_import_excel_dialog,
                    tag="import_excel_menu_item",
                )  # 添加导入Excel列菜单项

            with dpg.menu(
                label=self.texts[self.language]["editor_menu"], tag="editor_menu"
            ):  # 创建编辑器菜单
                dpg.add_menu_item(
                    label=self.texts[self.language]["settings"],
                    callback=self.show_settings_dialog,
                    tag="settings_menu_item",
                )  # 添加设置菜单项

    def create_table_window(self):  # 创建表格窗口函数
        with dpg.child_window(  # 创建子窗口
            width=-1, height=-1, horizontal_scrollbar=True, tag="Table Window"
        ):
            self.table_id = dpg.add_table(  # 添加表格
                header_row=True,  # 表头行
                resizable=False,  # 不可调整大小
                borders_innerH=True,  # 内部水平边框
                borders_outerH=True,  # 外部水平边框
                borders_innerV=True,  # 内部垂直边框
                borders_outerV=True,  # 外部垂直边框
                policy=dpg.mvTable_SizingFixedFit,  # 固定列宽
            )

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
            dpg.add_button(
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("column_dialog"),
                tag="close_column_dialog_button",
            )  # 添加关闭按钮

        with dpg.window(
            label=self.texts[self.language]["delete_row_dialog"],
            show=False,
            tag="row_dialog",
        ):  # 创建删除行对话框
            dpg.add_input_int(
                label=self.texts[self.language]["row_index"], tag="row_index"
            )  # 添加输入框，用于输入行索引
            dpg.add_button(
                label=self.texts[self.language]["delete"],
                callback=self.delete_row_by_index,
                tag="delete_row_button",
            )  # 添加按钮，用于删除行
            dpg.add_button(
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("row_dialog"),
                tag="close_row_dialog_button",
            )  # 添加关闭按钮

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
            dpg.add_button(
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("column_delete_dialog"),
                tag="close_column_delete_dialog_button",
            )  # 添加关闭按钮

        with dpg.window(
            label=self.texts[self.language]["edit_column_dialog"],
            show=False,
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
            tag="settings_dialog",
        ):  # 创建设置对话框
            dpg.add_checkbox(
                label=self.texts[self.language]["enable_feature"],
                tag="enable_feature_checkbox",
            )  # 添加复选框，用于启用功能
            dpg.add_button(
                label=self.texts[self.language]["apply"],
                callback=self.apply_settings,
                tag="apply_settings_button",
            )  # 添加按钮，用于应用设置
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
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("settings_dialog"),
                tag="close_settings_dialog_button",
            )  # 添加关闭按钮

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
            dpg.add_button(
                label=self.texts[self.language]["close"],
                callback=lambda: dpg.hide_item("import_excel_dialog"),
                tag="close_import_excel_dialog_button",
            )  # 添加关闭按钮

    def resize_callback(self, sender, app_data):  # 视口大小调整回调函数
        width, height = (
            dpg.get_viewport_client_width(),
            dpg.get_viewport_client_height(),
        )  # 获取视口宽度和高度
        dpg.set_item_width("Main Window", width)  # 设置主窗口宽度
        dpg.set_item_height("Main Window", height)  # 设置主窗口高度
        dpg.set_item_width("Table Window", width - 20)  # 设置表格窗口宽度
        dpg.set_item_height("Table Window", height - 60)  # 设置表格窗口高度

    def update_table(self):  # 更新表格函数
        dpg.delete_item(self.table_id, children_only=True)  # 删除表格中的所有子项
        if self.df is None:  # 如果数据框为空，返回
            return

        columns = list(self.df.columns)  # 获取数据框的列名
        total_width = len(columns) * self.column_width  # 计算表格总宽度

        dpg.set_item_width(self.table_id, total_width)  # 设置表格宽度

        for col in columns:  # 设置表格列
            dpg.add_table_column(
                label=col, parent=self.table_id, width=self.column_width
            )  # 添加表格列

        with dpg.table_row(parent=self.table_id):  # 添加数据类型选项
            for col in columns:
                dpg.add_combo(
                    items=["string", "int", "float", "bool"],
                    default_value=self.column_types.get(col, "string"),
                    user_data=col,
                    callback=self.change_column_type,
                )  # 添加下拉框，用于选择列类型

        for index, row in self.df.iterrows():  # 添加数据行
            with dpg.table_row(parent=self.table_id):
                for col in columns:
                    if self.column_types.get(col) == "bool":
                        dpg.add_combo(
                            items=["True", "False"],
                            default_value="True" if row[col] else "False",
                            user_data=(index, col),
                            callback=self.edit_cell,
                            width=self.column_width,
                        )  # 添加下拉框，用于选择布尔值
                    else:
                        dpg.add_input_text(
                            default_value=str(row[col]),
                            callback=self.edit_cell,
                            user_data=(index, col),
                            width=self.column_width,
                        )  # 添加输入框，用于输入文本

    def show_add_row_dialog(self):  # 显示添加行对话框函数
        dpg.show_item("row_dialog")  # 显示对话框
        dpg.focus_item("row_dialog")  # 使对话框获得焦点

    def show_add_column_dialog(self):  # 显示添加列对话框函数
        dpg.show_item("column_dialog")  # 显示对话框
        dpg.focus_item("column_dialog")  # 使对话框获得焦点

    def show_delete_row_dialog(self):  # 显示删除行对话框函数
        dpg.show_item("row_dialog")  # 显示对话框
        dpg.focus_item("row_dialog")  # 使对话框获得焦点

    def show_delete_column_dialog(self):  # 显示删除列对话框函数
        dpg.show_item("column_delete_dialog")  # 显示对话框
        dpg.focus_item("column_delete_dialog")  # 使对话框获得焦点

    def show_open_file_dialog(self):  # 显示打开文件对话框函数
        dpg.hide_item("file_dialog_id")
        dpg.show_item("file_dialog_id")  # 显示对话框
        dpg.focus_item("file_dialog_id")  # 使对话框获得焦点

    def show_settings_dialog(self):  # 显示设置对话框函数
        dpg.show_item("settings_dialog")  # 显示对话框
        dpg.focus_item("settings_dialog")  # 使对话框获得焦点

    def show_import_excel_dialog(self):  # 显示导入Excel列对话框函数
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
        is_enabled = dpg.get_value("enable_feature_checkbox")  # 获取启用功能复选框的值
        if is_enabled:
            self.set_file_association()  # 设置文件关联
        else:
            self.remove_file_association()  # 移除文件关联
        self.show_message(
            f"Settings applied. Feature enabled: {is_enabled}"
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
        dpg.set_item_label(self.save_menu_item, self.texts[self.language]["save_json"])

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

    def run(self):  # 运行函数
        dpg.start_dearpygui()  # 启动Dear PyGui
        dpg.destroy_context()  # 销毁Dear PyGui上下文


if __name__ == "__main__":  # 主程序入口
    app = JsonEditorApp()  # 创建JsonEditorApp实例
    app.run()  # 运行应用程序
