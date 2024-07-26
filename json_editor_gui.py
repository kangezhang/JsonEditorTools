# 版权声明：本脚本由 [zhang kang] 于 2024年7月开发，保留所有权利。
# 源码地址：https://github.com/kangezhang/JsonEditorTools
# 本代码仅供学习和参考。
# Copyright (c) 2024 zhang kang All rights reserved.
# -*- coding: utf-8 -*-

import dearpygui.dearpygui as dpg  # 导入Dear PyGui库，用于创建图形用户界面
import platform  # 导入platform模块，用于检测操作系统
from json_editor_functions import JsonEditorFunctions  # 导入JsonEditorFunctions类
import pandas as pd  # 导入pandas库，用于数据处理


class JsonEditorApp(
    JsonEditorFunctions
):  # 定义JsonEditorApp类，继承自JsonEditorFunctions
    def __init__(self):  # 初始化函数
        super().__init__(dpg)  # 调用父类的初始化函数
        self.column_width = 150  # 每列的固定宽度
        self.language = "Chinese"  # 默认语言为英语
        self.index_color_differentiation = False  # 初始化为不启用索引颜色区分
        dpg.create_context()  # 创建Dear PyGui上下文

        dpg.create_viewport(  # 创建视口
            title="JSON Editor",  # 视口标题
            width=1024,  # 视口宽度
            height=640,  # 视口高度
            resizable=True,  # 视口可调整大小
            small_icon="ico.ico",  # 小图标
            large_icon="ico.ico",  # 大图标
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

        self.texts = JsonEditorFunctions.languageDirc  # 获取语言字典

        with dpg.window(  # 创建主窗口
            label=self.texts[self.language]["main_window"],  # 主窗口标签
            no_title_bar=True,  # 无标题栏
            no_resize=True,  # 不可调整大小
            no_move=True,  # 不可移动
            no_collapse=True,  # 不可折叠
            no_close=True,  # 不可关闭
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

    def create_menu(self):  # 创建菜单函数
        with dpg.menu_bar():  # 创建菜单栏
            with dpg.menu(
                label=self.texts[self.language]["file_menu"], tag="file_menu"
            ):  # 创建文件菜单
                dpg.add_menu_item(
                    label="Open JSON", callback=self.show_open_file_dialog
                )
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
                    callback=self.add_row,
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
                self.setting_menu_item = dpg.add_menu_item(
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

    def update_table(self):  # 更新表格函数
        dpg.delete_item(self.table_id, children_only=True)  # 删除表格中的所有子项
        if self.df is None:  # 如果数据框为空，返回
            return

        columns = list(self.df.columns)  # 获取数据框的列名
        if self.index_color_differentiation and "ColorDisplay" not in columns:
            columns.append("ColorDisplay")
            self.df["ColorDisplay"] = "#000000"  # 默认颜色
        total_width = (
            len(columns) + 1
        ) * self.column_width  # 计算表格总宽度 (包含索引列)

        dpg.set_item_width(self.table_id, total_width)  # 设置表格宽度

        dpg.add_table_column(
            label="", parent=self.table_id, width=self.column_width
        )  # 添加索引列

        for col in columns:  # 设置表格列
            dpg.add_table_column(
                label=col, parent=self.table_id, width=self.column_width
            )  # 添加表格列

        with dpg.table_row(parent=self.table_id):  # 添加数据类型选项
            dpg.add_text("Type")  # 添加索引列的标题
            for col in columns:
                dpg.add_combo(
                    items=["string", "int", "float", "bool", "color"],
                    default_value=self.column_types.get(col, "string"),
                    user_data=col,
                    callback=self.change_column_type,
                    width=self.column_width,
                )  # 添加下拉框，用于选择列类型

        for index, row in self.df.iterrows():  # 添加数据行
            with dpg.table_row(parent=self.table_id):
                if self.index_color_differentiation:
                    color = row["ColorDisplay"]
                else:
                    color = "#FFFFFF"
                color_rgb = [int(color[i : i + 2], 16) for i in (1, 3, 5)]
                dpg.add_text(str(index), color=color_rgb)  # 添加行索引并设置颜色
                for col in columns:
                    if self.column_types.get(col) == "bool":
                        dpg.add_combo(
                            items=["True", "False"],
                            default_value="True" if row[col] else "False",
                            user_data=(index, col),
                            callback=self.edit_cell,
                            width=self.column_width,
                        )  # 添加下拉框，用于选择布尔值
                    elif self.column_types.get(col) == "color":
                        dpg.add_button(
                            label=row[col],
                            callback=self.show_color_picker,
                            user_data=(index, col),
                        )
                    else:
                        dpg.add_input_text(
                            default_value=str(row[col]),
                            callback=self.edit_cell,
                            user_data=(index, col),
                            width=self.column_width,
                        )  # 添加输入框，用于输入文本

    def run(self):  # 运行函数
        dpg.start_dearpygui()  # 启动Dear PyGui
        dpg.destroy_context()  # 销毁Dear PyGui上下文


if __name__ == "__main__":  # 主程序入口
    app = JsonEditorApp()  # 创建JsonEditorApp实例
    app.run()  # 运行应用程序
