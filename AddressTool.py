#! python3
# -*- coding: utf-8 -*-
#第一行注释是为了告诉Linux/OS X系统，这是一个Python可执行程序，Windows系统会忽略这个注释；
#第二行注释是为了告诉Python解释器，按照UTF-8编码读取源代码，否则，你在源代码中写的中文输出可能会有乱码
# Author: lizile
__author__ = 'lizile'

#pip install pynput
import sys
import xml.etree.ElementTree as ET
import os
import time
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog,
    QMessageBox, QCompleter, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QFrame,
    QScrollArea, QSizePolicy, QGridLayout, QTextEdit, QMenuBar
)
from PyQt6.QtCore import Qt, QFileSystemWatcher, QTimer
from PyQt6.QtGui import QPainter, QPixmap, QIcon, QColor, QFont, QLinearGradient, QBrush, QPen

RANGE_define = 20  # 定义变量数

# Apple 风格 QSS 样式表（纯样式，不改变任何布局与功能）
APPLE_QSS = """
/* ===== 全局背景 + 字体 ===== */
QWidget {
    background-color: #F0F0F5;
    color: #1D1D1F;
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* ===== 按钮统一风格 ===== */
QPushButton {
    background-color: #F2F2F7;
    color: #1D1D1F;
    border: 1px solid #E0E0E5;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #E5E5EA;
    border: 1px solid #C7C7CC;
}

QPushButton:pressed {
    background-color: #D1D1D6;
}

/* 主要按钮（刷新） — 蓝色实心 */
QPushButton#refreshBtn {
    background-color: #007AFF;
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}

QPushButton#refreshBtn:hover {
    background-color: #0066D6;
}

QPushButton#refreshBtn:pressed {
    background-color: #0055B3;
}

/* 局部刷新按钮 — 绿色 */
QPushButton#partialRefreshBtn {
    background-color: #34C759;
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}

QPushButton#partialRefreshBtn:hover {
    background-color: #2DB84D;
}

QPushButton#partialRefreshBtn:pressed {
    background-color: #28A745;
}

/* 一键清除按钮 — 红色 */
QPushButton#clearAllBtn {
    background-color: #FF3B30;
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}

QPushButton#clearAllBtn:hover {
    background-color: #E0352B;
}

QPushButton#clearAllBtn:pressed {
    background-color: #C02E25;
}

/* 常用变量按钮 — 浅橙色底 */
QPushButton#commonVarBtn {
    background-color: #FFF0E0;
    color: #C86500;
    border: 1px solid #F0D0B0;
    font-weight: 600;
}

QPushButton#commonVarBtn:hover {
    background-color: #FFE4CC;
    border: 1px solid #E8C098;
}

QPushButton#commonVarBtn:pressed {
    background-color: #FFD8B8;
}

/* 变量前缀按钮 — 浅蓝色底 */
QPushButton#prefixBtn {
    background-color: #E8F4FD;
    color: #0070C0;
    border: 1px solid #C0DCF0;
    font-weight: 600;
}

QPushButton#prefixBtn:hover {
    background-color: #D4ECFA;
    border: 1px solid #A8CCE8;
}

QPushButton#prefixBtn:pressed {
    background-color: #C0E0F5;
}

/* ===== 输入框 ===== */
QLineEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #D1D1D6;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
    color: #1D1D1F;
    selection-background-color: #007AFF;
    selection-color: #FFFFFF;
}

QLineEdit:focus {
    border: 1.5px solid #007AFF;
    background-color: #FAFAFF;
}

QLineEdit[readOnly="true"] {
    background-color: #F5F5F8;
    color: #6D6D72;
    border: 1.5px solid #E8E8ED;
}

/* ===== 滚动区域 ===== */
QScrollArea {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 10px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #C8C8CE;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #AEAEB2;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ===== 对话框 ===== */
QDialog {
    background-color: #F0F0F5;
}

QDialog QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 8px;
    padding: 4px;
    font-size: 13px;
    outline: none;
}

QDialog QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
}

QDialog QListWidget::item:selected {
    background-color: #007AFF;
    color: #FFFFFF;
}

QDialog QListWidget::item:hover:!selected {
    background-color: #F2F2F7;
}

QDialog QPushButton {
    background-color: #F2F2F7;
    color: #1D1D1F;
    border: 1px solid #E5E5EA;
    border-radius: 6px;
    padding: 7px 18px;
}

QDialog QPushButton:hover {
    background-color: #E5E5EA;
}

/* ===== 分隔线 ===== */
QFrame#rowSeparator {
    color: #E0E0E5;
}

/* ===== 提示框 ===== */
QToolTip {
    background-color: #1D1D1F;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

import logging

logging.basicConfig(level=logging.DEBUG)

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

# logging.debug('debug级别，一般用来打印一些调试信息，级别最低')
# logging.info('info级别，一般用来打印一些正常的操作信息')
# logging.warning('waring级别，一般用来打印警告信息')
# logging.error('error级别，一般用来打印一些错误信息')
# logging.critical('critical级别，一般用来打印一些致命的错误信息，等级最高')



class ArrayVariable:
    def __init__(self, var_name):
        self.base_name = ""
        self.indices = []
        self.dimension_sizes = []
        self.parse_var_name(var_name)
        self.base_address = 0
        self.offset_address = 0
        self.calculated_address = 0
        self.idref = 0
        self.byte_size = 0      #   数组大小
        self.array_size = 0     #   二维数组大小
        self.typeidref = 0      #   数组类型的typeId
        self.die_name = 0
        self.array_type = 0     # 0是正常的二维数组  #1是结构体二维数组
        self.element_byte_size = 0
        self.element_byte_size_idref = 0    # 数组的bytesize的id
        self.element_size = 0

    #   判断数组是一维度还是二维，并计算二维数组大小 
    #   解析一个带有数组索引的变量名，提取出变量的基础名称和数组索引信息
    def parse_var_name(self, var_name):
        name_parts = var_name.split('[')
        self.base_name = name_parts[0]
        for part in name_parts[1:]:
            index = part.strip(']')
            if index.isdigit():
                self.indices.append(int(index))
            else:
                raise ValueError("Invalid array index")
        if len(self.indices) == 2:
            self.dimension_sizes = [self.indices[0] + 1, self.indices[1] + 1]


    # 计算二维数组的偏移地址
    def calculate_offset_address(self, type_sizes,A):
        # 1.先找到数据类型大小
        if A == 1:
            element_size =  int(self.element_byte_size, 16) # 说明找到数据类型大小
        elif self.die_name in type_sizes:
            element_size = type_sizes[self.die_name]
        else:
            return None

        if not self.indices:
            return None

        byte_size_decimal = int(self.byte_size, 16)

        if len(self.indices) == 1:                      # 一维数组计算
            if (element_size * (self.indices[0] + 1)) > byte_size_decimal:
                return None
            self.offset_address = element_size * self.indices[0]

        elif len(self.indices) == 2:                    # 二维数组计算
            if not self.dimension_sizes or len(self.dimension_sizes) < 2:
                return None

            row_index, col_index = self.indices
            if row_index >= self.dimension_sizes[0] or col_index >= self.dimension_sizes[1]:
                return None

            row_size = self.indices[0] * int(self.array_size, 16)
            total_size =  ((self.indices[1] + 1)  + row_size ) * element_size

            if total_size > byte_size_decimal:
                return None

            row_size = self.indices[0] * int(self.array_size, 16)
            total_size = ((self.indices[1] + 1)  + row_size ) * element_size

            self.offset_address = total_size - element_size
        else:
            return None

        return self.offset_address

#######################################################################
# @brief 函数名称：get_global_variable_address                      
# @todo 代码实现的功能: 实现全局变量搜索
#                       1.轮训xml文件里面的symbol，找到symbol里面name和变量名字一样的symbol
#                       2.找到该symbol里面的value值，这个值就是变量首地址
#@param 参数：1.xml文件解析 2.变量名字
#@return 说明：int
#@retval 1. 返回全局变量地址
####################################################################
def _is_eabi_format(dwarf_info):
    """检测 XML 是否为 ofd2000 生成的 EABI/ELF 格式"""
    return dwarf_info.find('.//elf32_ehdr') is not None


def _find_dwarf_value(die, attr_name):
    """查找 DWARF 属性的值文本，兼容 ofd6x (<block>) 和 ofd2000 (<exprloc>)

    自动过滤栈/寄存器相对地址（DW_OP_bregXX / DW_OP_fbreg），
    这些是编译器优化到栈上的变量，没有固定内存地址，返回 None 避免给出无意义的栈偏移值。
    """
    for tag in ('exprloc', 'block'):
        elem = die.find(f".//attribute[type='{attr_name}']/value/{tag}")
        if elem is not None and elem.text is not None:
            if 'DW_OP_breg' in elem.text or 'DW_OP_fbreg' in elem.text:
                return None
            return elem.text
    return None


def get_global_variable_address(dwarf_info, var_name):
    symbol_table = dwarf_info.find('.//symbol_table')
    is_eabi = _is_eabi_format(dwarf_info)

    if symbol_table is not None:
        if is_eabi:
            # ofd2000 EABI/ELF: <elf32_sym> → <st_name_string>/<st_value>, 无 _ 前缀
            for sym in symbol_table.iter('elf32_sym'):
                name_elem = sym.find('st_name_string')
                if name_elem is not None and name_elem.text == var_name:
                    bind_elem = sym.find('st_bind')
                    if bind_elem is not None and bind_elem.text != 'STB_GLOBAL':
                        continue
                    value_elem = sym.find('st_value')
                    if value_elem is not None:
                        return int(value_elem.text, 16)
        else:
            # ofd6x COFF: <symbol> → <name>/<value>, 有 _ 前缀
            var_name_with_prefix = f"_{var_name}"
            for symbol in symbol_table.iter('symbol'):
                name_element = symbol.find('name')
                if name_element is not None and name_element.text == var_name_with_prefix:
                    value_element = symbol.find('value')
                    if value_element is not None:
                        return int(value_element.text, 16)

    # DWARF DIE 回退查找（静态局部变量等，兼容 ofd6x 和 ofd2000）
    for die in dwarf_info.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == var_name:
            text = _find_dwarf_value(die, 'DW_AT_location')
            if text is not None:
                value_element = text.split()[-1]
                if value_element is not None:
                    return int(value_element, 16)
    return None

#######################################################################
# @brief 函数名称：get_struct_member_offset                    
# @todo 代码实现的功能: 查询结构体变量的偏移地址
#                      
####################################################################
def get_struct_member_offset(dwarf_info, base_address, struct_name, member_name):
    for die in dwarf_info.iter('die'):                                              # 轮询die
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == member_name:                 # 找到与变量名一样的id
            text = _find_dwarf_value(die, 'DW_AT_data_member_location')             # 兼容 ofd6x/ofd2000
            if text is not None:
                offset_value = text.split()[-1]
                offset = int(offset_value, 16)
                return base_address + offset
    return None

#######################################################################
# @brief 函数名称：get_variable_address_array                    
# @todo 代码实现的功能: 查询结构体的变量地址
#                      
####################################################################
def get_variable_address_recursive(xml_file, var_name):
    names = var_name.split('.')
    base_address = get_global_variable_address(xml_file, names[0])

    if base_address is None:
        return None

    for i in range(1, len(names)):
        base_address = get_struct_member_offset(xml_file, base_address, names[i - 1], names[i])
        if base_address is None:
            return None

    return base_address

#######################################################################
# @brief 函数名称：get_variable_baseaddress_regular_array                    
# @todo 代码实现的功能: 
#                      找基地址
####################################################################
def get_variable_baseaddress_regular_array(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == array_var.base_name:
            text = _find_dwarf_value(die, 'DW_AT_location')
            if text is not None:
                base_value = text.split()[-1]
                base = int(base_value, 16)

                type_attr = die.find(".//attribute[type='DW_AT_type']/value/ref")
                if type_attr is not None:
                    array_var.idref = type_attr.get("idref")
                    return base
    return None

#######################################################################
# @brief 函数名称：get_variable_type_regular_array                 
# @todo 代码实现的功能: 找到数组类型的名字                      
####################################################################
def get_variable_type_regular_array(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.idref:        #遍历die 找到 idref  最后找到 数组类型的typeidref
            array_var.typeidref = die.find(".//attribute[type='DW_AT_type']/value/ref")
            if array_var.typeidref is not None:
                array_var.typeidref = array_var.typeidref.get('idref')
                array_var.byte_size = die.find(".//attribute[type='DW_AT_byte_size']/value/const").text

                # If it's an array type, find the DW_TAG_array_type DIE and get the byte size  
                # 查找二维数组的大小
                for die in dwarf_info.iter('die'):
                    if die.get('id') == array_var.idref:
                        array_var.typeidref = die.find(".//attribute[type='DW_AT_type']/value/ref")
                        if array_var.typeidref is not None:
                            array_var.typeidref = array_var.typeidref.get('idref')

                        byte_size_element = die.find(".//attribute[type='DW_AT_byte_size']/value/const")
                        if byte_size_element is not None:
                            array_var.byte_size = byte_size_element.text # 数组大小
                            
                        A = 0
                        for sub_die in die.findall('die'):
                            A = A+1 
                            if A == 2:             # 二维数组 中 二维的大小对应第二个die里面的参数
                                for attribute in sub_die.findall('attribute'):
                                    value = attribute.find('value/const')
                                    if value is not None:
                                        array_var.array_size = int(value.text, 16) + 1
                                        array_var.array_size = hex(array_var.array_size)  # 拿到的数组大小要+1


                # 在 .debug_pubtypes section 中查找 name_table
                for section in dwarf_info.iter('section'):
                    section_name = section.find('name')
                    if section_name is not None and section_name.text == ".debug_pubtypes":
                        name_table = section.find('name_table')
                        if name_table is not None:
                            for name in name_table.iter('name'):
                                ref = name.find("ref")
                                if ref is not None and ref.get('idref') == array_var.typeidref:
                                    die_name = name.find("die_name")
                                    if die_name is not None:
                                        array_var.die_name = die_name.text
                                        return array_var.die_name
    return None


#######################################################################
# @brief 函数名称：get_variable_type_regular_array_element_byte_size                  
# @todo 代码实现的功能: #通过xml文件查找数组数据类型大小
#@return 说明：1 说明找到数组类型大小   0 没找到数组类型大小
####################################################################
def get_variable_type_regular_array_element_byte_size(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.typeidref:
            name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
            if name_attr is not None and name_attr.text is not None:
                if array_var.die_name == name_attr.text:
                    type_attr = die.find(".//attribute[type='DW_AT_type']/value/ref")
                    array_var.element_byte_size_idref = type_attr.get("idref")
                    break 

    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.element_byte_size_idref:
            DW_AT_byte_size_TEMP = die.find(".//attribute[type='DW_AT_byte_size']/value/const")
            if DW_AT_byte_size_TEMP is not None: 
                if die.find(".//attribute[type='DW_AT_byte_size']/value/const").text is not None: 
                    array_var.element_byte_size = die.find(".//attribute[type='DW_AT_byte_size']/value/const").text
                return 1     
                
    return None

#######################################################################
# @brief 函数名称：get_variable_offsetaddress_regular_array                    
# @todo 代码实现的功能: 
#                      
#       return： 返回基地址
####################################################################
def get_variable_offsetaddress_regular_array(dwarf_info, array_var, type_sizes):
    # 查找数组的类型和二维数组的大小
    die_name = get_variable_type_regular_array1(dwarf_info, array_var)
    if die_name is None:
        return None
    A = get_variable_type_regular_array_element_byte_size(dwarf_info, array_var)
    return array_var.calculate_offset_address(type_sizes,A)

#######################################################################
# @brief 函数名称：get_variable_address_regular_array                    
# @todo 代码实现的功能: 
#                      通过数组名，找到基地址和偏移地址，并计算总地址
####################################################################
def get_variable_address_regular_array(xml_file, var_name, type_sizes):
    array_var = ArrayVariable(var_name)
    # 通过数组名，找到基地址和 数组的类型idref
    array_var.base_address = get_variable_baseaddress_regular_array(xml_file, array_var)
    if array_var.base_address is None:
        return None
    
    Returnresult = None
    # 找到数组类型的名字：后面找不到数据类型大小，就用名字人为进行偏移
    array_var.die_name = get_variable_type_regular_array1(xml_file, array_var) 
    if array_var.die_name is None:
        Returnresult = get_variable_type_regular_array_element_byte_size(xml_file, array_var)

    # Returnresult = 1 用xml找到的数据类型大小偏移 0 则用自己定义的数据类型大小偏移
    offset_address = array_var.calculate_offset_address(type_sizes,Returnresult) # 计算二维数组的偏移地址
    if offset_address is None:
        return None
    
    address = array_var.base_address  + offset_address
    return address


#######################################################################
# @brief 函数名称：get_variable_address_struct_array_offset                    
# @todo 代码实现的功能: 
#                      找到数组在结构体的偏移地址 和 数组的类型idref
#@param 参数：1.xml_file 
#             2.变量名字
#             3.struct_name 结构体名称
#             4.member_name 结构体变量名称 
#             5.               
#@return 说明：int
#@retval 1. 二级变量的偏移地址
#        2. 数据类型
####################################################################
def get_variable_address_struct_array_offset(xml_file, base_address, struct_name, member_name, type_sizes):

    array_name = member_name.split('[')[0]   #数组名称
    #######################################################################
    #  struct_type_idref  
    #  通过结构体名称，找到该结构体的 DW_AT_type 类型                                
    ####################################################################
    struct_type_idref = None
    for die in xml_file.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == struct_name:
            type_attr = die.find(".//attribute[type='DW_AT_type']/value/ref")
            if type_attr is not None:
                struct_type_idref = type_attr.get("idref")
                break

    if struct_type_idref is None:
        return None
    
    #######################################################################
    #  array_type_idref  
    #       通过结构体的 DW_AT_type 类型  查询到二级变量 member_name 结构体定义
    #  1. 并保存二级变量的偏移地址  struct_offset 
    #       从变量体里面找到二级变量die   从die中DW_AT_type 找到变量数据类型
    #  2.找到变量的数据类型   array_type_idref                         
    ####################################################################
    struct_offset = None
    array_type_idref = None
    for die in xml_file.iter('die'):
        if die.get('id') == struct_type_idref:      # 根据结构体名称的ideref 找到对应的die
            DW_AT_type_die = die.find(".//attribute[type='DW_AT_type']/value/ref")
            if DW_AT_type_die is not None:
                DW_AT_type_die_struct_type_idref = DW_AT_type_die.get("idref")

            for member_die in die.iter('die'):      # 从结构体die里面 轮询 变量die
                if member_die.find('tag').text == "DW_TAG_member":
                    member_name_attr = member_die.find(".//attribute[type='DW_AT_name']/value/string")
                    if member_name_attr is not None and member_name_attr.text == array_name:       # 找到和变量名字一样的 变量die
                        text = _find_dwarf_value(member_die, 'DW_AT_data_member_location')    #找到变量的相对于结构体的偏移地址
                        if text is not None:
                            offset_value = text.split()[-1]
                            struct_offset = int(offset_value, 16)   # 转成16进制

                        type_attr = member_die.find(".//attribute[type='DW_AT_type']/value/ref") #  找到变量的数据类型
                        if type_attr is not None:
                            array_type_idref = type_attr.get("idref")
                            break    

    #######################################################################
    #   若上面的方法找不到 array_type_idref
    #   则通过   DW_AT_type_die_struct_type_idref  继续找
    #   TODO：估计是某些数组会有嵌套的原因，具体忘记了                
    ####################################################################
                            
    if  array_type_idref is None:
        for die in xml_file.iter('die'):
            if die.get('id') == DW_AT_type_die_struct_type_idref:      # 根据结构体名称的ideref 找到对应的die
                for member_die in die.iter('die'):      # 从结构体die里面 轮询 变量die
                    if member_die.find('tag').text == "DW_TAG_member":
                        member_name_attr = member_die.find(".//attribute[type='DW_AT_name']/value/string")
                        if member_name_attr is not None and member_name_attr.text == array_name:       # 找到和变量名字一样的 变量die
                            text = _find_dwarf_value(member_die, 'DW_AT_data_member_location')    #找到变量的相对于结构体的偏移地址
                            if text is not None:
                                offset_value = text.split()[-1]
                                struct_offset = int(offset_value, 16)   # 转成16进制

                            type_attr = member_die.find(".//attribute[type='DW_AT_type']/value/ref")#找到变量的数据类型
                            if type_attr is not None:
                                array_type_idref = type_attr.get("idref")
                                break 
                                   
    if struct_offset is None or array_type_idref is None:
        return None
    return struct_offset, array_type_idref


#######################################################################
# @brief 函数名称：get_variable_type_regular_array1                  
# @todo 代码实现的功能: 
#               数组变量类型的名字 --  UINT16  UINT32                     
####################################################################
def get_variable_type_regular_array1(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.idref:    #
            array_var.typeidref = die.find(".//attribute[type='DW_AT_type']/value/ref")
            if array_var.typeidref is not None:
                array_var.typeidref = array_var.typeidref.get('idref')       #遍历die 找到 idref  最后找到 数组类型的typeidref

            #######################################################################
            # array_var.byte_size = 数组字节大小                                    
            ####################################################################
            byte_size_element = die.find(".//attribute[type='DW_AT_byte_size']/value/const")
            if byte_size_element is not None:
                array_var.byte_size = byte_size_element.text
            else:   #假如当前的数组类型找不到，就需要根据数组类型的idref重新轮训
                for die in dwarf_info.iter('die'):
                    if die.get('id') == array_var.typeidref:
                        byte_size_element = die.find(".//attribute[type='DW_AT_byte_size']/value/const")
                        if byte_size_element is not None:
                            array_var.byte_size = byte_size_element.text
                            break

            #######################################################################
            # array_var.array_size = 二维数组第二个数组大小  
            # TODO：这里应该可以优化，attribute 中的die 对于二维数组来看，第一个die的 value/const 是第一维的大小，第二个是第二维的大小
            #       想要实现三维数组的话，这里应该可以实现                               
            ####################################################################                       
            A = 0
            for sub_die in die.findall('die'):
                A = A+1 
                if A == 2:             # 二维数组 中 二维的大小对应第二个die里面的参数
                    for attribute in sub_die.findall('attribute'):
                        value = attribute.find('value/const')
                        if value is not None:
                            array_var.array_size = int(value.text, 16) + 1
                            array_var.array_size = hex(array_var.array_size)  # 拿到的数组大小要+1
                            break

            #######################################################################
            # array_var.die_name = 找到数组的变量数据类型的名字                                  
            #################################################################### 

            # 假设 dwarf_info 是你的 ElementTree.Element 对象，这里简化示例
            for section in dwarf_info.iter('section'):
                section_name = section.find('name')
                if section_name is not None and section_name.text == ".debug_pubtypes":
                    # 遍历每一个 name_table
                    for name_table in section.iter('name_table'):
                        if name_table is not None:
                            for name in name_table.iter('name'):
                                ref = name.find("ref")
                                if ref is not None and ref.get('idref') == array_var.typeidref:
                                    die_name = name.find("die_name")
                                    if die_name is not None:
                                        array_var.die_name = die_name.text
                                        return array_var.die_name   #找到数组的变量数据类型的名字
                                    
            typeidref_const = None
            #######################################################################
            # 跑到这里没找到变量数据类型的名字，那数组可能是常量Const数组  
            # 需要通过 typeidref 找到   typeidref_const  里面的ref                                    
            ####################################################################                  
            for die in dwarf_info.iter('die'):
                if die.get('id') == array_var.typeidref:
                    typeidref_const = die.find(".//attribute[type='DW_AT_type']/value/ref")
                    if typeidref_const is not None:
                        typeidref_const = typeidref_const.get('idref')

                        for die in dwarf_info.iter('die'):
                            if die.get('id') == typeidref_const:
                                DW_AT_type = die.find(".//attribute[type='DW_AT_type']/value/ref")        
                                if DW_AT_type is not None:

                                    # 找到最后的 idref 后，就开始查找变量名字
                                    DW_AT_type = DW_AT_type.get('idref')   
                                    for section in dwarf_info.iter('section'):
                                        section_name = section.find('name')
                                        if section_name is not None and section_name.text == ".debug_pubtypes":
                                            # 遍历每一个 name_table
                                            for name_table in section.iter('name_table'):
                                                if name_table is not None:
                                                    for name in name_table.iter('name'):
                                                        ref = name.find("ref")
                                                        if ref is not None and ref.get('idref') == DW_AT_type:
                                                            die_name = name.find("die_name")
                                                            if die_name is not None:
                                                                array_var.die_name = die_name.text
                                                                return array_var.die_name   #找到数组的变量数据类型的名字
                                                           
                        break
            #######################################################################
            # array_var.die_name = 找到数组的变量数据类型的名字      兼容集中式储能                              
            #################################################################### 
            # 假设 dwarf_info 是你的 ElementTree.Element 对象，这里简化示例
            for die in dwarf_info.iter('die'):
                if die.get('id') == array_var.typeidref:
                    die_name = die.find(".//attribute[type='DW_AT_name']/value/string")
                    if die_name is not None:
                        array_var.die_name   = die_name.text
                        return array_var.die_name
         
    return None

#######################################################################
# @brief 函数名称：get_variable_address_struct_array                  
# @todo 代码实现的功能: 查询带数组，且是结构体下的变量地址
#                      1.先通过结构体查找基地址
#                      2.找到数组在结构体的偏移地址和 数组的类型idref    
####################################################################
DEBUGTemp1 = 0
DEBUGTemp = 0
def get_variable_address_struct_array(root, var_name, type_sizes):
    names = var_name.split('.')
    names_length = len(names)  # 获取列表长度
    base_address = get_global_variable_address(root, names[0])  #求出结构体名称的基地址   
    if base_address is None:
        return None

    #######################################################################
    # 找到数组在结构体的偏移地址和 数组的类型idref                            
    ####################################################################  
    if names_length <= 2: 
        struct_offset, array_type_idref = get_variable_address_struct_array_offset(root, base_address, names[0], names[1],
                                                                                type_sizes)  # '0x8a:0x4bd31'
    elif names_length == 3:  # 结构体嵌套的情况，先找到2级变量的偏移地址
        struct_offset_0 = None
        for die in root.iter('die'):
            name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
            if name_attr is not None and name_attr.text == names[1]:                # 找到与变量名一样的name
                text = _find_dwarf_value(die, 'DW_AT_data_member_location')
                if text is not None:
                    value_element = text.split()[-1]                         # 第二个参数就是变量地址
                    if value_element is not None:
                        struct_offset_0 =  int(value_element, 16)    

        struct_offset_1, array_type_idref = get_variable_address_struct_array_offset(root, base_address, names[1], names[2],
                                                                            type_sizes)  # '0x8a:0x4bd31' 
        struct_offset  = struct_offset_0 + struct_offset_1


    #######################################################################
    # 通过   变量数据类型 计算出当前变量的 数组偏移地址                              
    ####################################################################  
    array_var = ArrayVariable(var_name) #创建对象
    array_var.idref = array_type_idref

    die_name = get_variable_type_regular_array1(root, array_var) # 找到数组类型的名字：后面找不到数据类型大小，就用名字人为进行偏移
    if die_name is None:
        return None
    Returnresult = get_variable_type_regular_array_element_byte_size(root, array_var) #通过xml文件查找数组数据类型大小
    # Returnresult = 1 用xml找到的数据类型大小偏移 0 则用自己定义的数据类型大小偏移
    
    offset_address = array_var.calculate_offset_address(type_sizes,Returnresult) # 计算二维数组的偏移地址
    if offset_address is None:
        return None

    address = base_address + struct_offset + offset_address
    return address

#######################################################################
# @brief 函数名称：get_variable_address_array                    
# @todo 代码实现的功能: 查询带数组的变量地址
#                      区分名字是否存在结构体
####################################################################
def get_variable_address_array(root, var_name, type_sizes):
    if '.' in var_name:
        # Process array within a structure
        return get_variable_address_struct_array(root, var_name, type_sizes)
    else:
        # Process regular array
        return get_variable_address_regular_array(root, var_name, type_sizes)


#######################################################################
# @brief 函数名称：get_variable_address                    
# @todo 代码实现的功能: 查询地址函数总入口 
#                      区分变量名是否带数组标识
#TODO：总入口
####################################################################
def get_variable_address(root, var_name, type_sizes):
    if '[' in var_name:
        return get_variable_address_array(root, var_name, type_sizes)   #查询带数组的变量地址
    elif '.' in var_name:
        return get_variable_address_recursive(root, var_name)
    else:
        return get_global_variable_address(root, var_name)


def find_file_in_directory(directory, filename):
    for root, _, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def load_type_sizes(self):
    # 初始化默认数据类型和变量前缀
    default_type_sizes = {
        "int16": 1,
        "int32": 2,
        "int64": 4,
        "Uint16": 1,
        "Uint32": 2,
        "Uint64": 4,
        "float32": 2,
        "float64": 4,
        "Uint8": 1,
        "short": 1,
        "USHORT": 1,
        "DWORD": 2,
        "INT16": 1,
        "INT32": 2,
        "INT64": 4,
        "UINT16": 1,
        "UINT32": 2,
        "UINT64": 4,
        "FLOAT32": 2,
        "FLOAT64": 4,

        # 你可以在这里添加更多默认的数据类型及其大小
    }
    default_variables = [
        "objADCDrv.",
        "objCMPSSDrv.",
        "objFlashDrv.",
        "objPIEDrv.",
        "objGPIODrv.",
        "objPWMDrv.",
        "objRAMDrv.",
        "objSCIDrv.",
        "objSysDrv.",
        "objDMADrv.",
        "objXBarDrv.",
        "objCANDrv.",
        "objSPIDrv.",
        "objTimerDrv.",
        "objWatchDogDrv.",
        "objECapDrv.",
        "objGridPower.",
        "objInvAlgorithm.",
        "objInvCtrl.",
        "objSysLogic.",
        "objDCBus.",
        "objSwitchLogic.",
        "objDigitalIO.",
        "objCpuTimerDrv.",
        "objI2CDrv.",
        "objCLADrv.",
        "objDSPRunStat.",
        "objTemperature.",
        "objSciaApp.",
        "objMonitor.",
        "objSyncLogic.",
        "objCanApp.",
        "objMasterCpApp.",
        # 你可以在这里添加更多默认的变量前缀
    ]

    type_sizes = default_type_sizes.copy()
    variables = default_variables.copy()
    common_variables = {}  # 存储常用变量
    Control_variables = {}  # 存储控制变量
    Memory_variables = {}  # 存储历史变量

    start_marker = "# 数据类型_开始行"
    end_marker = "# 数据类型_结束行"
    var_start_marker = "# 常用变量_开始行"
    var_end_marker = "# 常用变量_结束行"
    Controlvar_start_marker = "# 控制变量_开始行"
    Controlvar_end_marker = "# 控制变量_结束行"
    prefix_start_marker = "# 变量前缀_开始行"
    prefix_end_marker = "# 变量前缀_结束行"
    VarMemory_start_marker = "# 变量存储_开始行"
    VarMemory_end_marker = "# 变量存储_结束行"

    reading_sizes = False
    reading_vars = False
    reading_prefixes = False
    reading_Controlvars = False
    reading_VarMemory = False

    # 获取当前脚本或EXE的目录
    if getattr(sys, 'frozen', False):
        current_directory = os.path.dirname(sys.executable)
    else:
        current_directory = os.path.dirname(os.path.abspath(__file__))

    # 查找当前目录下的 type_sizes.txt 文件
    file_path = os.path.join(current_directory, 'type_sizes.txt')
    if not os.path.exists(file_path):
        ##QMessageBox.warning(self, "警告", f"当前路径下未找到 type_sizes.txt 文件\n当前路径: {current_directory}")
        return type_sizes, variables, common_variables
            
    try:
        with open(file_path, 'r') as file:
            file_type_sizes = {}
            file_variables = []
            VAR_variables = []
            for line in file:
                line = line.strip()
                if line == start_marker:
                    reading_sizes = True
                    continue
                elif line == end_marker:
                    reading_sizes = False
                    continue
                elif line == var_start_marker:
                    reading_vars = True
                    continue
                elif line == var_end_marker:
                    reading_vars = False
                    continue
                elif line == prefix_start_marker:
                    reading_prefixes = True
                    continue
                elif line == prefix_end_marker:
                    reading_prefixes = False
                    continue
                elif line == Controlvar_start_marker:
                    reading_Controlvars = True
                    continue
                elif line == Controlvar_end_marker:
                    reading_Controlvars = False
                    continue  
                elif line == VarMemory_start_marker:
                    reading_VarMemory = True
                    continue
                elif line == VarMemory_end_marker:
                    reading_VarMemory = False
                    continue

                if reading_sizes:
                    parts = line.split('=')
                    if len(parts) == 2:
                        type_name, size_str = parts
                        type_name = type_name.strip()
                        size = int(size_str.strip())
                        file_type_sizes[type_name] = size
                
                if reading_vars:
                    parts = line.split(':')
                    if len(parts) == 2:
                        cn_name, var_name = parts
                        common_variables[cn_name.strip()] = var_name.strip()

                if reading_Controlvars:
                    parts = line.split(':')
                    if len(parts) == 2:
                        Control_cn_name, Control_var_name = parts
                        Control_variables[Control_cn_name.strip()] = Control_var_name.strip()

                if reading_prefixes:
                    file_variables.append(line)

                if reading_VarMemory:
                    VAR_variables.append(line)
            # 如果文件中有数据，则使用文件中的数据
            if file_type_sizes:
                type_sizes = file_type_sizes
            if file_variables:
                variables = file_variables
            if VAR_variables:
                Memory_variables = VAR_variables

    except Exception as e:
        print(f"加载type_sizes.txt时发生错误: {e}")
        #QMessageBox.warning(self, "警告", "加载type_sizes.txt时发生错误")
    return type_sizes, variables, common_variables,Control_variables,Memory_variables  # 增加返回 common_variables




def convert_out_to_xml(ofd6x_path, out_file):
    xml_file = os.path.splitext(out_file)[0] + ".xml"
    cmd = f'"{ofd6x_path}" --xml --dwarf "{out_file}" > "{xml_file}"'

    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"执行命令时发生错误: {e}")
        return None

    return xml_file


def parse_dwarf_xml(xml_file):
    try:
        # 修复：先读取文件内容（支持中文路径），再解析XML
        with open(xml_file, 'r', encoding='utf-8', errors='replace') as f:
            xml_content = f.read()
        # 手动解析内容，避免ET.parse对中文路径的兼容问题
        root = ET.fromstring(xml_content)
        return root
    except ET.ParseError as e:
        print(f"解析XML文件时发生错误: {e}")
        return None
    except FileNotFoundError:
        print(f"文件未找到: {xml_file}")
        return None
    except Exception as e:
        print(f"读取文件时发生未知错误: {e}")
        return None
    

#######################################################################
# @brief 函数名称：write_var_to_memory_block                   
# @todo 代码实现的功能: 适配GB2312编码，清空并写入 # 变量存储_开始行 和 # 变量存储_结束行 之间的内容
#    :param file_path: txt文件路径
#    :param var_names: 要写入的变量名列表（非空的var_name）
####################################################################
def write_var_to_memory_block(file_path, var_names):
   
    # 固定标记（和你的txt格式完全一致）
    start_tag = "# 变量存储_开始行"
    end_tag = "# 变量存储_结束行"

    # 1. 读取文件（GB2312编码，忽略解码错误）
    lines = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='gb2312') as f:
                lines = [line.rstrip('\n') for line in f]  # 保留每行内容，去掉换行符
        except Exception as e:
            print(f"读取文件（GB2312）：{e}，尝试忽略错误读取")
            with open(file_path, 'r', encoding='gb2312', errors='ignore') as f:
                lines = [line.rstrip('\n') for line in f]

    # 2. 定位开始/结束标记的位置
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == start_tag:
            start_idx = i
        elif line.strip() == end_tag:
            end_idx = i

    # 3. 构建新内容（清空标记间旧内容，写入新变量名）
    new_lines = []
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        # 保留开始标记前的内容
        new_lines.extend(lines[:start_idx+1])
        # 写入新变量名（每行一个，匹配你的格式）
        new_lines.extend(var_names)
        # 保留结束标记及之后的内容
        new_lines.extend(lines[end_idx:])
    else:
        # 没找到标记，直接追加到文件末尾
        new_lines = lines + [start_tag] + var_names + [end_tag]

    # 4. 写入文件（固定GB2312编码）
    try:
        with open(file_path, 'w', encoding='gb2312') as f:
            f.write('\n'.join(new_lines))
        print(f"✅ 成功写入 {len(var_names)} 个变量到：{file_path}")
    except Exception as e:
        print(f"❌ 写入失败：{e}")


def update_specific_line_in_txt(file_path, line_idx, new_var_name):
    """
    精准更新TXT中 # 变量存储_开始行 和 # 变量存储_结束行 之间的指定行
    :param file_path: txt文件路径
    :param line_idx: 要更新的行索引（从0开始，比如第5行=4）
    :param new_var_name: 新的变量名（空则写空字符串）
    """
    # 固定标记
    start_tag = "# 变量存储_开始行"
    end_tag = "# 变量存储_结束行"
    encoding = "gb2312"

    # 1. 读取文件并拆分内容
    all_lines = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                all_lines = [line.rstrip('\n') for line in f]
        except Exception as e:
            print(f"读取文件失败：{e}")
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                all_lines = [line.rstrip('\n') for line in f]

    # 2. 定位标记区间，提取原有变量行
    start_idx = -1
    end_idx = -1
    # 找标记位置
    for i, line in enumerate(all_lines):
        if line.strip() == start_tag:
            start_idx = i
        elif line.strip() == end_tag:
            end_idx = i

    # 初始化标记区间内的变量行（无则创建空列表）
    var_lines = []
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        # 提取标记间的所有行（即原有变量列表）
        var_lines = all_lines[start_idx+1 : end_idx]

    # 3. 精准更新指定行（索引对应）
    # 若要更新的行索引超出当前列表长度，补空行直到对应索引
    if line_idx >= len(var_lines):
        # 补空行（保证索引对应）
        for _ in range(len(var_lines), line_idx + 1):
            var_lines.append("")
    # 替换指定行的内容
    var_lines[line_idx] = new_var_name.strip()

    # 4. 重构文件内容（保留标记+更新后的变量行）
    new_all_lines = []
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        # 保留开始标记前的内容
        new_all_lines.extend(all_lines[:start_idx+1])
        # 写入更新后的变量行
        new_all_lines.extend(var_lines)
        # 保留结束标记及之后的内容
        new_all_lines.extend(all_lines[end_idx:])
    else:
        # 无标记则创建标记+变量行（补空行到指定索引）
        var_lines = [""] * (line_idx + 1)
        var_lines[line_idx] = new_var_name.strip()
        new_all_lines = all_lines + [start_tag] + var_lines + [end_tag]

    # 5. 写回文件
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write('\n'.join(new_all_lines))
        print(f"✅ 成功更新TXT第{line_idx+1}行：{new_var_name}")
    except Exception as e:
        print(f"❌ 更新失败：{e}")





def _create_app_icon():
    """生成 App 图标：蓝紫渐变圆角方形 + 白色 A 字母"""
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 蓝紫渐变背景圆角方形
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor("#007AFF"))
    gradient.setColorAt(1.0, QColor("#5856D6"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(8, 8, size - 16, size - 16, 48, 48)

    # 白色 A 字母
    painter.setPen(QColor("#FFFFFF"))
    font = QFont("Segoe UI", 120, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A")

    painter.end()
    return QIcon(pixmap)


class AddressFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(_create_app_icon())
        self.type_sizes, self.variables, self.common_variables, self.Control_variables , self.Memory_variables = load_type_sizes(self)  # 获取常用变量
        self.xml_file = None
        self.setStyleSheet(APPLE_QSS)
        self.setAcceptDrops(True)
        self.initUI()
        self.previous_variables = [""] * RANGE_define
        self._disable_child_drops(self)

    def _disable_child_drops(self, parent):
        """禁用所有子控件的拖放，让拖放事件冒泡到主窗口处理"""
        for child in parent.findChildren(QWidget):
            child.setAcceptDrops(False)

    def _drag_has_out_file(self, event):
        """检查拖拽事件是否包含单个 .out 文件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().lower().endswith('.out'):
                return True
        return False

    def dragEnterEvent(self, event):
        if self._drag_has_out_file(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self._drag_has_out_file(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self._drag_has_out_file(event):
            out_path = event.mimeData().urls()[0].toLocalFile()
            self.out_input.setText(out_path)
            self.start_watch_out_file(out_path)
            self.refresh_xml_file()
            self.log("拖拽导入", f"已加载 OUT 文件: {os.path.basename(out_path)}", "success")
            event.acceptProposedAction()
        else:
            event.ignore()

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于 AddressTool",
            f"<h3>OUT文件取址工具</h3>"
            f"<p>版本: V20260525</p>"
            f"<p>公司: Sineng</p>"
            f"<p>作者: Lancer</p>"
        )

    def initUI(self):
        self.setWindowTitle("OUT文件取址工具")
        self.setGeometry(100, 100, 1700, 920)
        self.setMinimumSize(1450, 800)

        # ===== 顶层布局：菜单栏 + 主界面 =====
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 菜单栏
        menubar = QMenuBar()
        menubar.setStyleSheet("""
            QMenuBar { background: #E8E8ED; border-bottom: 1px solid #D1D1D6; padding: 2px 8px; font-size: 13px; }
            QMenuBar::item { padding: 4px 12px; border-radius: 4px; }
            QMenuBar::item:selected { background: #D1D1D6; }
            QMenu { background: #F5F5F7; border: 1px solid #D1D1D6; border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 6px 24px; border-radius: 4px; }
            QMenu::item:selected { background: #007AFF; color: white; }
        """)
        # 日志开关（菜单栏左侧，与"帮助"统一样式）
        log_menu = menubar.addMenu("日志")
        self.log_action = log_menu.addAction("显示日志面板")
        self.log_action.setCheckable(True)
        self.log_action.triggered.connect(lambda checked: self.log_widget.setVisible(checked))
        help_menu = menubar.addMenu("帮助")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)
        main_layout.addWidget(menubar)

        # ===== 顶级水平布局：左侧日志 + 右侧主界面 =====
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(12, 14, 12, 14)
        outer_layout.setSpacing(12)

        # ========== 左侧日志面板 ==========
        self.log_widget = QWidget()
        self.log_widget.setVisible(False)  # 默认隐藏，点击"日志"按钮后显示
        log_panel = QVBoxLayout(self.log_widget)
        log_panel.setContentsMargins(0, 0, 0, 0)
        log_panel.setSpacing(8)

        log_title_layout = QHBoxLayout()
        log_title = QLabel("操作日志")
        log_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #1D1D1F; background: transparent;")
        log_title_layout.addWidget(log_title)
        log_title_layout.addStretch()
        self.clear_log_button = QPushButton("清空")
        self.clear_log_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_log_button.clicked.connect(self.clear_log)
        self.clear_log_button.setStyleSheet("""
            QPushButton {
                background-color: #F2F2F7; color: #8E8E93; border: 1px solid #E5E5EA;
                border-radius: 6px; padding: 4px 12px; font-size: 12px;
            }
            QPushButton:hover { background-color: #E5E5EA; }
        """)
        log_title_layout.addWidget(self.clear_log_button)
        log_panel.addLayout(log_title_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumWidth(300)
        self.log_output.setMaximumWidth(340)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFC;
                border: 1px solid #E8E8ED;
                border-radius: 10px;
                padding: 10px 14px;
                font-family: "Cascadia Code", "Consolas", "Microsoft YaHei", monospace;
                font-size: 12px;
                color: #1D1D1F;
                selection-background-color: #007AFF;
                selection-color: #FFFFFF;
            }
            QScrollBar:vertical {
                width: 6px; background: transparent;
            }
            QScrollBar::handle:vertical {
                background-color: #C8C8CE; border-radius: 3px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background-color: #AEAEB2; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        log_panel.addWidget(self.log_output, 1)
        outer_layout.addWidget(self.log_widget)

        # ========== 右侧主界面（原有全部内容） ==========
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Top info layout
        top_layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        self.TODO_label = QLabel("TODO: 不支持二维数组以上的搜索;  局部刷新只会更新名称有变化的变量;")
        self.TODO_label1 = QLabel("系数   U16变量:0    电流:336     电网电压:690   母线电压:1200")
        info_layout.addWidget(self.TODO_label)
        info_layout.addWidget(self.TODO_label1)

        self.Var_refres_button = QPushButton("变量记录")
        self.Var_refres_button.clicked.connect(self.Var_refres)
        self.Var_refres_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.clear_all_button = QPushButton("一键清除变量")
        self.clear_all_button.setObjectName("clearAllBtn")
        self.clear_all_button.clicked.connect(self.clear_all_variables)
        self.clear_all_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setObjectName("refreshBtn")
        self.refresh_button.clicked.connect(self.refresh_addresses)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.partial_refresh_button = QPushButton("局部刷新")
        self.partial_refresh_button.setObjectName("partialRefreshBtn")
        self.partial_refresh_button.clicked.connect(self.partial_refresh_addresses)
        self.partial_refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.refresh_xml_button = QPushButton("刷新XML文件")
        self.refresh_xml_button.clicked.connect(self.refresh_xml_file)
        self.refresh_xml_button.setCursor(Qt.CursorShape.PointingHandCursor)

        top_layout.addLayout(info_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.Var_refres_button)
        top_layout.addWidget(self.clear_all_button)
        top_layout.addWidget(self.refresh_button)
        top_layout.addWidget(self.partial_refresh_button)
        top_layout.addWidget(self.refresh_xml_button)

        layout.addLayout(top_layout)

        # ofd6x path input
        ofd6x_layout = QHBoxLayout()
        self.default_path_button = QPushButton("默认路径")
        self.default_path_button.clicked.connect(self.set_default_ofd6x_path)
        self.default_path_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ofd6x_label = QLabel("ofd工具路径:")
        self.ofd6x_input = QLineEdit()
        self.ofd6x_input.setPlaceholderText("选择或输入 ofd2000.exe / ofd6x.exe 的路径...")
        self.ofd6x_browse = QPushButton("浏览")
        self.ofd6x_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ofd6x_browse.clicked.connect(self.browse_ofd6x)
        ofd6x_layout.addWidget(self.default_path_button)
        ofd6x_layout.addWidget(self.ofd6x_label)
        ofd6x_layout.addWidget(self.ofd6x_input)
        ofd6x_layout.addWidget(self.ofd6x_browse)
        layout.addLayout(ofd6x_layout)

        # out file path input
        out_layout = QHBoxLayout()
        self.out_label = QLabel("OUT文件路径:")
        self.out_input = QLineEdit()
        self.out_input.setPlaceholderText("选择或拖拽 .out 文件到窗口...")
        self.out_browse = QPushButton("浏览")
        self.out_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.out_browse.clicked.connect(self.browse_out)
        out_layout.addWidget(self.out_label)
        out_layout.addWidget(self.out_input)
        out_layout.addWidget(self.out_browse)
        layout.addLayout(out_layout)

        # XML update info output
        self.xml_update_label = QLabel("XML更新信息:")
        self.xml_update_output = QLineEdit()
        self.xml_update_output.setReadOnly(True)
        self.xml_update_output.setPlaceholderText("等待刷新...")
        xml_update_layout = QHBoxLayout()
        xml_update_layout.addWidget(self.xml_update_label)
        xml_update_layout.addWidget(self.xml_update_output)
        layout.addLayout(xml_update_layout)


        # Variable names input (move to a scrollable area, use grid layout for compactness)
        # Variable names input (默认 20 行，可追加更多)
        self.var_labels = []
        self.var_inputs = []
        self.addr_labels = []
        self.addr_outputs = []
        self.sn_addr_labels = []
        self.sn_addr_outputs = []

        completer = QCompleter(self.variables)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # 添加变量按钮（用于超出20行时追加）
        self.add_var_button = QPushButton("添加变量")
        self.add_var_button.clicked.connect(self.add_variable_row)
        self.add_var_button.setCursor(Qt.CursorShape.PointingHandCursor)
        top_layout.addWidget(self.add_var_button)

        # container widget for entries
        entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(entries_widget)
        self.entries_layout.setSpacing(6)
        self.entries_layout.setContentsMargins(6, 6, 6, 6)

        # create initial RANGE_define rows
        for i in range(RANGE_define):
            self._create_variable_row(completer)

        # make it scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(entries_widget)
        scroll.setMinimumHeight(300)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(scroll)

        outer_layout.addLayout(layout, 1)
        main_layout.addLayout(outer_layout)

        # 启动日志
        self.log("工具启动", "就绪 — 等待操作")

        # 文件监控：监视 OUT 文件变化以自动刷新
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_out_file_changed)

        # Automatically find ofd6x tool and out file if possible
        A = self.auto_find_tools()
        if A is not None:
            out_path = self.out_input.text().strip()
            if out_path:
                self.start_watch_out_file(out_path)
            self.refresh_xml_file()

    # ===== 日志方法 =====
    def log(self, tag, msg, level="info"):
        """向左侧日志面板追加一条带时间戳的日志。

        level: 'info' (蓝) | 'success' (绿) | 'warn' (橙) | 'error' (红)
        """
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info":    "#007AFF",
            "success": "#34C759",
            "warn":    "#FF9500",
            "error":   "#FF3B30",
        }
        color = colors.get(level, "#8E8E93")
        html = (
            f'<p style="margin:2px 0;">'
            f'<span style="color:#8E8E93;">[{ts}]</span> '
            f'<span style="color:{color};font-weight:600;">[{tag}]</span> '
            f'<span style="color:#1D1D1F;">{msg}</span>'
            f'</p>'
        )
        self.log_output.append(html)
        # 自动滚动到底部
        bar = self.log_output.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear_log(self):
        self.log_output.clear()
        self.log("工具", "日志已清空")

    def show_variable_dialog(self, idx):
        dialog = QDialog(self)
        dialog.setWindowTitle("选择变量前缀")
        layout = QVBoxLayout(dialog)

        var_list = QListWidget(dialog)
        for var in self.variables:
            item = QListWidgetItem(var)
            var_list.addItem(item)

        # 6. 定义「选中变量后的回调函数」（核心逻辑）
        def on_var_selected():
            selected_items = var_list.selectedItems()
            if selected_items:
                self.var_inputs[idx].setText(selected_items[0].text())
            dialog.accept()

        #绑定「列表项双击事件」：双击列表项时触发选中逻辑
        var_list.itemDoubleClicked.connect(on_var_selected)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(on_var_selected)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(var_list)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def _create_variable_row(self, completer):
        idx = len(self.var_inputs)

        # create widgets
        label = QLabel(f"变量名称{idx + 1}:")
        var_input = QLineEdit()
        var_input.setCompleter(completer)
        var_input.setPlaceholderText("输入变量名...")
        var_input.setMinimumWidth(500)

        select_prefix_button = QPushButton("变量前缀")
        select_prefix_button.setObjectName("prefixBtn")
        select_prefix_button.clicked.connect(lambda _, i=idx: self.show_variable_dialog(i))
        select_prefix_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_common_var_button = QPushButton("常用变量")
        select_common_var_button.setObjectName("commonVarBtn")
        select_common_var_button.clicked.connect(lambda _, i=idx: self.show_common_variable_dialog(i))
        select_common_var_button.setCursor(Qt.CursorShape.PointingHandCursor)

        sn_label = QLabel("软件示波器地址:")
        sn_output = QLineEdit()
        sn_output.setReadOnly(True)
        sn_output.setPlaceholderText("—")
        sn_output.setMinimumWidth(90)
        sn_output.setMaximumWidth(110)

        addr_label = QLabel("MAP地址:")
        addr_output = QLineEdit()
        addr_output.setReadOnly(True)
        addr_output.setPlaceholderText("—")
        addr_output.setMinimumWidth(90)
        addr_output.setMaximumWidth(110)

        # append to lists
        self.var_labels.append(label)
        self.var_inputs.append(var_input)
        self.sn_addr_labels.append(sn_label)
        self.sn_addr_outputs.append(sn_output)
        self.addr_labels.append(addr_label)
        self.addr_outputs.append(addr_output)

        # layout for this row (keep original horizontal spacing)
        row_layout = QHBoxLayout()
        row_layout.addWidget(select_common_var_button)
        row_layout.addWidget(select_prefix_button)
        row_layout.addWidget(label)
        row_layout.addWidget(var_input)
        row_layout.addWidget(sn_label)
        row_layout.addWidget(sn_output)
        row_layout.addWidget(addr_label)
        row_layout.addWidget(addr_output)

        self.entries_layout.addLayout(row_layout)

        # add separator after every 4 rows
        if (idx + 1) % 4 == 0:
            sep = QFrame()
            sep.setObjectName("rowSeparator")
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFrameShadow(QFrame.Shadow.Plain)

            self.entries_layout.addWidget(sep)

        # update previous_variables length
        self.previous_variables = [""] * len(self.var_inputs)

    def add_variable_row(self):
        # allow adding unlimited rows
        completer = QCompleter(self.variables)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._create_variable_row(completer)

    def start_watch_out_file(self, path: str):
        """开始监控指定的 OUT 文件路径（仅当文件存在时）"""
        if not path:
            return
        # 移除之前的监听
        try:
            existing = self.file_watcher.files()
            if existing:
                self.file_watcher.removePaths(existing)
        except Exception:
            pass

        # 添加新的监听
        try:
            if os.path.exists(path):
                self.file_watcher.addPath(path)
        except Exception:
            pass

    def on_out_file_changed(self, path: str):
        """文件变化回调：延迟处理以等待写入完成，然后刷新 XML 与地址"""
        # 延迟 600ms 再处理，避免文件写入未完成
        QTimer.singleShot(600, lambda: self._handle_out_file_change(path))

    def _handle_out_file_change(self, path: str):
        # 如果文件不存在，直接返回；否则尝试刷新 xml 并更新地址
        if not path or not os.path.exists(path):
            try:
                if path:
                    self.file_watcher.addPath(path)
            except Exception:
                pass
            return

        self.log("文件监控", "检测到 OUT 文件变化，自动刷新...", "info")
        # 重新调用刷新逻辑
        try:
            self.refresh_xml_file()
            # 小延迟后刷新地址，确保 xml 已生成
            QTimer.singleShot(300, self.refresh_addresses)
        finally:
            # 确保 watcher 继续监听该文件（某些平台 fileChanged 只触发一次）
            try:
                if path not in self.file_watcher.files():
                    self.file_watcher.addPath(path)
            except Exception:
                pass

#######################################################################
# @brief 函数名称：show_common_variable_dialog                    
# @todo 代码实现的功能: 
#                      常用变量按钮的QT界面实现
####################################################################
    def show_common_variable_dialog(self, idx):
        dialog = QDialog(self)
        dialog.setWindowTitle("选择常用变量")
        layout = QVBoxLayout(dialog)

        var_list = QListWidget(dialog)
        for cn_name in self.common_variables:
            item = QListWidgetItem(cn_name)
            var_list.addItem(item)

        def on_var_selected():
            selected_items = var_list.selectedItems()
            if selected_items:
                cn_name = selected_items[0].text()
                en_name = self.common_variables[cn_name]
                self.var_inputs[idx].setText(en_name)
            dialog.accept()

        var_list.itemDoubleClicked.connect(on_var_selected)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(on_var_selected)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(var_list)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def browse_ofd6x(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择ofd工具路径",
            filter="ofd工具 (ofd2000.exe ofd6x.exe);;可执行文件 (*.exe)")
        if path:
            self.ofd6x_input.setText(path)

    def browse_out(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择OUT文件路径")
        if path:
            self.out_input.setText(path)
            # 开始监控所选 out 文件
            try:
                self.start_watch_out_file(path)
            except Exception:
                pass

    def Var_refres(self):
        loop_count = min(len(self.Memory_variables), len(self.var_inputs))
        for idx in range(loop_count):
            self.var_inputs[idx].setText(self.Memory_variables[idx])
        self.log("变量记录", f"已加载 {loop_count} 个历史变量到输入框")

    def clear_all_variables(self):
        """一键清空所有变量输入框和地址输出框"""
        cleared = 0
        for i in range(len(self.var_inputs)):
            if self.var_inputs[i].text().strip():
                self.var_inputs[i].clear()
                self.addr_outputs[i].clear()
                self.sn_addr_outputs[i].clear()
                self.previous_variables[i] = ""
                cleared += 1
        if cleared > 0:
            self.log("清除变量", f"已清空 {cleared} 个变量输入及地址", "warn")
        else:
            self.log("清除变量", "当前没有需要清除的变量", "info")

    def refresh_addresses(self):
        valid_var_names = []
        self.log("全量刷新", "开始刷新全部变量...")
        self.refresh_xml_file()
        if not self.xml_file or not os.path.exists(self.xml_file):
            self.log("全量刷新", "XML 文件生成失败，请检查 ofd6x 和 OUT 路径", "error")
            return
        dwarf_info = parse_dwarf_xml(self.xml_file)
        if dwarf_info is None:
            self.log("全量刷新", "XML 解析失败，刷新中止", "error")
            return
        found_count = 0
        miss_count = 0
        for i in range(len(self.var_inputs)):
            var_name = self.var_inputs[i].text().strip()
            if var_name:
                address = get_variable_address(dwarf_info, var_name, self.type_sizes)
                if address is not None:
                    self.addr_outputs[i].setText(hex(address))
                    sn_address = address - 0x8000
                    data2 = hex(sn_address)[2:]
                    self.sn_addr_outputs[i].setText(data2)
                    self.log("变量", f"#{i+1} '{var_name}' → MAP: {hex(address)}, 示波器: {data2}", "success")
                    found_count += 1
                else:
                    self.addr_outputs[i].setText("未找到/数组地址越界")
                    self.sn_addr_outputs[i].setText("未找到/数组地址越界")
                    self.log("变量", f"#{i+1} '{var_name}' — 未找到/地址越界", "warn")
                    miss_count += 1
                self.previous_variables[i] = var_name
                valid_var_names.append(var_name)
            # TODO
        self.log("全量刷新", f"完成 — 找到 {found_count} 个, 未找到 {miss_count} 个", "success" if miss_count == 0 else "warn")
        current_directory = os.path.abspath(os.getcwd())
        txt_file_path = os.path.join(current_directory, 'type_sizes.txt')
        write_var_to_memory_block(txt_file_path, valid_var_names)

    def partial_refresh_addresses(self):
        if not self.xml_file or not os.path.exists(self.xml_file):
            self.log("局部刷新", "XML 文件不存在，请先刷新 XML", "error")
            return
        dwarf_info = parse_dwarf_xml(self.xml_file)
        if dwarf_info is None:
            self.log("局部刷新", "XML 解析失败，刷新中止", "error")
            return

        current_directory = os.path.abspath(os.getcwd())
        txt_file_path = os.path.join(current_directory, 'type_sizes.txt')

        changed_count = 0
        for i in range(len(self.var_inputs)):
            var_name = self.var_inputs[i].text().strip()
            if var_name != self.previous_variables[i]:
                address = get_variable_address(dwarf_info, var_name, self.type_sizes)
                if address is not None:
                    self.addr_outputs[i].setText(hex(address))
                    sn_address = address - 0x8000
                    data2 = hex(sn_address)[2:]
                    self.sn_addr_outputs[i].setText(data2)
                    self.log("局部刷新", f"#{i+1} '{var_name}' → MAP: {hex(address)}", "success")
                else:
                    self.addr_outputs[i].setText("未找到/数组地址越界")
                    self.sn_addr_outputs[i].setText("未找到/数组地址越界")
                    self.log("局部刷新", f"#{i+1} '{var_name}' — 未找到/地址越界", "warn")
                self.previous_variables[i] = var_name
                update_specific_line_in_txt(txt_file_path, line_idx=i, new_var_name=var_name)
                changed_count += 1
        if changed_count == 0:
            self.log("局部刷新", "没有检测到变化的变量", "info")
        else:
            self.log("局部刷新", f"完成 — 更新了 {changed_count} 个变量", "success")

    def refresh_xml_file(self):
        ofd6x_path = self.ofd6x_input.text().strip()
        out_file = self.out_input.text().strip()
        if not ofd6x_path or not out_file:
            self.log("XML", "请先设置 ofd6x 工具路径和 OUT 文件路径", "error")
            return
        self.xml_file = convert_out_to_xml(ofd6x_path, out_file)

        if self.xml_file:
            mod_time = time.ctime(os.path.getmtime(self.xml_file))
            self.xml_update_output.setText(f"最新修改日期: {mod_time}")
            self.log("XML", f"XML 已更新 — {mod_time}", "success")
        else:
            self.log("XML", "XML 刷新失败", "error")
            QMessageBox.warning(self, "错误", "刷新XML文件失败")

    def set_default_ofd6x_path(self):
        current_dir = os.path.abspath(os.getcwd())
        ofd_path = find_file_in_directory(current_dir, "ofd2000.exe") or \
                   find_file_in_directory(current_dir, "ofd6x.exe")
        if ofd_path:
            self.ofd6x_input.setText(ofd_path)
        else:
            QMessageBox.warning(self, "错误", "在当前路径下未找到 ofd2000.exe 或 ofd6x.exe")

    def auto_find_tools(self):
        # 获取当前工作目录的绝对路径
        current_directory = os.path.abspath(os.getcwd())

        # 优先查找 ofd2000.exe（支持 EABI），其次 ofd6x.exe（兼容 COFF）
        ofd_path = None
        for exe_name in ("ofd2000.exe", "ofd6x.exe"):
            files = [f for f in os.listdir(current_directory) if f == exe_name]
            if files:
                ofd_path = os.path.join(current_directory, files[0])
                break

        if ofd_path:
            self.ofd6x_input.setText(ofd_path)
        else:
            QMessageBox.warning(self, "警告", "当前路径下未找到 ofd2000.exe 或 ofd6x.exe 文件")
            return None

        # 查找当前目录下的 .out 文件
        out_files = [f for f in os.listdir(current_directory) if f.endswith('.out')]
        if out_files:
            # 假设我们选择第一个找到的 .out 文件
            out_file_path = os.path.join(current_directory, out_files[0])
            self.out_input.setText(out_file_path)
            # 开始监控自动发现的 out 文件
            try:
                self.start_watch_out_file(out_file_path)
            except Exception:
                pass
        else:
            #QMessageBox.warning(self, "警告", "当前路径下未找到任何 OUT 文件")
            return None
        
        return 1
    
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # 运行在打包的环境中
        current_dir = os.path.dirname(sys.executable)
    else:
         # 运行在开发环境中
        current_dir = os.path.dirname(os.path.abspath(__file__))
    # logging.debug('debug级别，一般用来打印一些调试信息，级别最低')    
    os.chdir(current_dir)
    app = QApplication(sys.argv)
    ex = AddressFinder()
    ex.show()
    sys.exit(app.exec())
