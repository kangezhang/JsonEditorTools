# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.
# -*- coding: utf-8 -*-

import tkinter as tk  # 导入tkinter模块，用于图形用户界面
from tkinter import filedialog, messagebox  # 从tkinter模块导入文件对话框和消息框
import dearpygui.dearpygui as dpg  # 导入Dear PyGui库，用于创建图形用户界面
import platform  # 导入platform模块，用于检测操作系统
from json_editor_functions import (
    JsonEditorFunctions,
)  # 从json_editor_functions模块导入JsonEditorFunctions类
import os


class JsonEditorApp(
    JsonEditorFunctions
):  # 定义JsonEditorApp类，继承自JsonEditorFunctions
    def __init__(self):  # 初始化函数
        super().__init__(dpg)  # 调用父类的初始化函数
        self.column_width = 150  # 每列的固定宽度

        dpg.create_context()  # 创建Dear PyGui上下文

        # 初始化视口
        dpg.create_viewport(
            title="JSON Editor",
            width=1024,
            height=640,
            resizable=True,
            small_icon="1.ico",
            large_icon="1.ico",
        )

        # 注册字体

        FONT = self.get_font_path()
        with dpg.font_registry():
            with dpg.font(FONT, 20) as ft:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.bind_font(ft)

        # 主窗口
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
            self.create_menu()  # 创建菜单
            self.create_table_window()  # 创建表格窗口

        # 创建对话框
        self.create_dialogs()  # 创建各种对话框

        # 设置 Dear PyGui
        dpg.setup_dearpygui()  # 设置Dear PyGui
        dpg.show_viewport()  # 显示视口

        # 设置窗口大小变化的回调函数
        dpg.set_viewport_resize_callback(
            self.resize_callback
        )  # 设置视口大小调整回调函数

    def get_font_path(self):  # 获取字体路径函数
        if platform.system() == "Windows":
            return "C:/Windows/Fonts/simhei.ttf"  # Arial字体路径
        elif platform.system() == "Darwin":  # macOS
            return "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS系统字体路径
        else:
            return (
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux系统字体路径
            )

    def create_menu(self):  # 创建菜单函数
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="打开 JSON", callback=self.open_json
                )  # 添加打开JSON菜单项
                self.save_menu_item = dpg.add_menu_item(
                    label="Save JSON",
                    callback=self.save_json,
                    enabled=False,  # 添加保存JSON菜单项，默认禁用
                )

            with dpg.menu(label="Edit"):
                dpg.add_menu_item(
                    label="Add Row", callback=self.add_row
                )  # 添加添加行菜单项
                dpg.add_menu_item(
                    label="Add Column",
                    callback=self.show_add_column_dialog,  # 添加添加列菜单项
                )
                dpg.add_menu_item(
                    label="Delete Row", callback=self.show_delete_row_dialog
                )  # 添加删除行菜单项
                dpg.add_menu_item(
                    label="Delete Column", callback=self.show_delete_column_dialog
                )  # 添加删除列菜单项

    def create_table_window(self):  # 创建表格窗口函数
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
                policy=dpg.mvTable_SizingFixedFit,  # 确保列宽固定
            )

    def create_dialogs(self):  # 创建对话框函数
        # 添加列对话框
        with dpg.window(label="Add Column", show=False, tag="column_dialog"):
            dpg.add_input_text(
                label="Column Name", tag="new_column_name"
            )  # 添加输入框，用于输入列名
            dpg.add_combo(
                label="Column Type",
                items=["string", "int", "float", "bool"],
                tag="new_column_type",  # 添加下拉框，用于选择列类型
            )
            dpg.add_button(
                label="Add", callback=self.add_column_name
            )  # 添加按钮，用于添加列

        # 删除行对话框
        with dpg.window(label="Delete Row", show=False, tag="row_dialog"):
            dpg.add_input_int(
                label="Row Index", tag="row_index"
            )  # 添加输入框，用于输入行索引
            dpg.add_button(
                label="Delete", callback=self.delete_row_by_index
            )  # 添加按钮，用于删除行

        # 删除列对话框
        with dpg.window(label="Delete Column", show=False, tag="column_delete_dialog"):
            dpg.add_input_text(
                label="Column Name", tag="column_name_delete"
            )  # 添加输入框，用于输入列名
            dpg.add_button(
                label="Delete", callback=self.delete_column_by_name
            )  # 添加按钮，用于删除列

        # 修改列名对话框
        with dpg.window(label="Edit Column Name", show=False, tag="edit_column_dialog"):
            dpg.add_input_text(
                label="Current Column Name", tag="current_column_name"
            )  # 添加输入框，用于输入当前列名
            dpg.add_input_text(
                label="New Column Name", tag="new_column_name_edit"
            )  # 添加输入框，用于输入新列名
            dpg.add_button(
                label="Rename", callback=self.edit_column_name
            )  # 添加按钮，用于重命名列

    def resize_callback(self, sender, app_data):  # 视口大小调整回调函数
        width, height = (
            dpg.get_viewport_client_width(),  # 获取视口宽度
            dpg.get_viewport_client_height(),  # 获取视口高度
        )
        dpg.set_item_width("Main Window", width)  # 设置主窗口宽度
        dpg.set_item_height("Main Window", height)  # 设置主窗口高度
        dpg.set_item_width("Table Window", width - 20)  # 留出一点空间以便水平滚动条
        dpg.set_item_height("Table Window", height - 60)  # 留出一些高度以便菜单和滚动条

    def update_table(self):  # 更新表格函数
        dpg.delete_item(self.table_id, children_only=True)  # 删除表格中的所有子项
        if self.df is None:  # 如果数据框为空，返回
            return

        columns = list(self.df.columns)  # 获取数据框的列名
        total_width = len(columns) * self.column_width  # 计算表格总宽度

        dpg.set_item_width(self.table_id, total_width)  # 设置表格宽度

        # 设置表格列
        for col in columns:
            dpg.add_table_column(
                label=col, parent=self.table_id, width=self.column_width  # 添加表格列
            )

        # 添加数据类型选项
        with dpg.table_row(parent=self.table_id):
            for col in columns:
                dpg.add_combo(
                    items=["string", "int", "float", "bool"],
                    default_value=self.column_types.get(col, "string"),
                    user_data=col,
                    callback=self.change_column_type,  # 添加下拉框，用于选择列类型
                )

        # 添加数据行
        for index, row in self.df.iterrows():
            with dpg.table_row(parent=self.table_id):
                for col in columns:
                    if self.column_types.get(col) == "bool":
                        dpg.add_combo(
                            items=["True", "False"],
                            default_value="True" if row[col] else "False",
                            user_data=(index, col),
                            callback=self.edit_cell,
                            width=self.column_width,  # 设置每个输入框的宽度
                        )
                    else:
                        dpg.add_input_text(
                            default_value=str(row[col]),
                            callback=self.edit_cell,
                            user_data=(index, col),
                            width=self.column_width,  # 设置每个输入框的宽度
                        )

    def show_add_column_dialog(self):  # 显示添加列对话框函数
        dpg.show_item("column_dialog")

    def show_delete_row_dialog(self):  # 显示删除行对话框函数
        dpg.show_item("row_dialog")

    def show_delete_column_dialog(self):  # 显示删除列对话框函数
        dpg.show_item("column_delete_dialog")

    def run(self):  # 运行函数
        dpg.start_dearpygui()  # 启动Dear PyGui
        dpg.destroy_context()  # 销毁Dear PyGui上下文


if __name__ == "__main__":  # 主程序入口
    app = JsonEditorApp()  # 创建JsonEditorApp实例
    app.run()  # 运行应用程序
