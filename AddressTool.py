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
    QMessageBox, QCompleter, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt

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
        self.byte_size = 0  #数组大小
        self.array_size = 0  #二维数组大小
        self.typeidref = 0  # 数组类型的typeId
        self.die_name = 0
        self.array_type = 0 # 0是正常的二维数组  #1是结构体二维数组
        self.element_byte_size = 0
        self.element_byte_size_idref = 0 # 数组的bytesize的id
        self.element_size = 0
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
        if A == 1:
            element_size =  int(self.element_byte_size, 16)
        elif self.die_name in type_sizes:
            element_size = type_sizes[self.die_name]
        else:
            return None

        if not self.indices:
            return None

        byte_size_decimal = int(self.byte_size, 16)

        if len(self.indices) == 1:
            if (element_size * (self.indices[0] + 1)) > byte_size_decimal:
                return None
            self.offset_address = element_size * self.indices[0]

        elif len(self.indices) == 2:
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
def get_global_variable_address(dwarf_info, var_name):
    # 查找<symbol_table>元素
    symbol_table = dwarf_info.find('.//symbol_table')  # 使用XPath查找第一个<symbol_table>
    if symbol_table is None:
        # 如果没有找到<symbol_table>，则返回None
        return None

    var_name_with_prefix = f"_{var_name}"           #名字前面 + _
    for symbol in symbol_table.iter('symbol'):
        name_element = symbol.find('name')
        if name_element is not None and name_element.text == var_name_with_prefix:
            value_element = symbol.find('value')
            if value_element is not None:
                return int(value_element.text, 16)
            
    # 上面方法没找到的话，变量可能是局部静态变量，需要用另外的方法找        
    for die in dwarf_info.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == var_name:                # 找到与变量名一样的name
            base_attr = die.find(".//attribute[type='DW_AT_location']/value/block")
            if base_attr is not None:
                value_element = base_attr.text.split()[-1]                         # 第二个参数就是变量地址
                if value_element is not None:
                    return int(value_element, 16)      
    return None


def get_struct_member_offset(dwarf_info, base_address, struct_name, member_name):
    for die in dwarf_info.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == member_name:
            offset_attr = die.find(".//attribute[type='DW_AT_data_member_location']/value/block")
            if offset_attr is not None:
                offset_value = offset_attr.text.split()[-1]
                offset = int(offset_value, 16)
                return base_address + offset
    return None


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


def get_variable_baseaddress_regular_array(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
        if name_attr is not None and name_attr.text == array_var.base_name:
            base_attr = die.find(".//attribute[type='DW_AT_location']/value/block")
            if base_attr is not None:
                base_value = base_attr.text.split()[-1]
                base = int(base_value, 16)

                type_attr = die.find(".//attribute[type='DW_AT_type']/value/ref")
                if type_attr is not None:
                    array_var.idref = type_attr.get("idref")
                    return base
    return None


def get_variable_type_regular_array(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.idref:
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
                            array_var.byte_size = byte_size_element.text
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

#通过xml文件查找数组数据类型大小
def get_variable_type_regular_array_element_byte_size(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.typeidref:
            name_attr = die.find(".//attribute[type='DW_AT_name']/value/string")
            if array_var.die_name == name_attr.text:
                type_attr = die.find(".//attribute[type='DW_AT_type']/value/ref")
                array_var.element_byte_size_idref = type_attr.get("idref")
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.element_byte_size_idref:
            array_var.element_byte_size = die.find(".//attribute[type='DW_AT_byte_size']/value/const").text
            return 1             
    return None

def get_variable_offsetaddress_regular_array(dwarf_info, array_var, type_sizes):
    # 查找数组的类型和二维数组的大小
    die_name = get_variable_type_regular_array(dwarf_info, array_var)
    if die_name is None:
        return None
    A = get_variable_type_regular_array_element_byte_size(dwarf_info, array_var)
    return array_var.calculate_offset_address(type_sizes,A)


def get_variable_address_regular_array(xml_file, var_name, type_sizes):
    array_var = ArrayVariable(var_name)
    # 通过数组名，找到基地址和 数组的类型idref
    array_var.base_address = get_variable_baseaddress_regular_array(xml_file, array_var)
    if array_var.base_address is None:
        return None
    offset_address = get_variable_offsetaddress_regular_array(xml_file, array_var, type_sizes)
    if offset_address is None:
        return None

    address = array_var.base_address + array_var.offset_address
    return address


def get_variable_address_struct_array_offset(xml_file, base_address, struct_name, member_name, type_sizes):
    array_name = member_name.split('[')[0]

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
                        offset_attr = member_die.find(".//attribute[type='DW_AT_data_member_location']/value/block")    #找到变量的相对于结构体的偏移地址
                        if offset_attr is not None:
                            offset_value = offset_attr.text.split()[-1]
                            struct_offset = int(offset_value, 16)   # 转成16进制

                        type_attr = member_die.find(".//attribute[type='DW_AT_type']/value/ref")#找到变量的数据类型
                        if type_attr is not None:
                            array_type_idref = type_attr.get("idref")

    if  array_type_idref is None:
        for die in xml_file.iter('die'):
            if die.get('id') == DW_AT_type_die_struct_type_idref:      # 根据结构体名称的ideref 找到对应的die
                for member_die in die.iter('die'):      # 从结构体die里面 轮询 变量die
                    if member_die.find('tag').text == "DW_TAG_member":
                        member_name_attr = member_die.find(".//attribute[type='DW_AT_name']/value/string")
                        if member_name_attr is not None and member_name_attr.text == array_name:       # 找到和变量名字一样的 变量die
                            offset_attr = member_die.find(".//attribute[type='DW_AT_data_member_location']/value/block")    #找到变量的相对于结构体的偏移地址
                            if offset_attr is not None:
                                offset_value = offset_attr.text.split()[-1]
                                struct_offset = int(offset_value, 16)   # 转成16进制

                            type_attr = member_die.find(".//attribute[type='DW_AT_type']/value/ref")#找到变量的数据类型
                            if type_attr is not None:
                                array_type_idref = type_attr.get("idref")
                                   
    if struct_offset is None or array_type_idref is None:
        return None
    return struct_offset, array_type_idref

# 找到数组类型的名字
def get_variable_type_regular_array1(dwarf_info, array_var):
    for die in dwarf_info.iter('die'):
        if die.get('id') == array_var.idref:
            array_var.typeidref = die.find(".//attribute[type='DW_AT_type']/value/ref")
            if array_var.typeidref is not None:
                array_var.typeidref = array_var.typeidref.get('idref')

            byte_size_element = die.find(".//attribute[type='DW_AT_byte_size']/value/const")
            if byte_size_element is not None:
                array_var.byte_size = byte_size_element.text
            A = 0
            for sub_die in die.findall('die'):
                A = A+1 
                if A == 2:             # 二维数组 中 二维的大小对应第二个die里面的参数
                    for attribute in sub_die.findall('attribute'):
                        value = attribute.find('value/const')
                        if value is not None:
                            array_var.array_size = int(value.text, 16) + 1
                            array_var.array_size = hex(array_var.array_size)  # 拿到的数组大小要+1

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
                                        return array_var.die_name
    return None


def get_variable_address_struct_array(root, var_name, type_sizes):
    names = var_name.split('.')
    #求出结构体名称的基地址
    base_address = get_global_variable_address(root, names[0])
    if base_address is None:
        return None

    # 找到数组在结构体的偏移地址和 数组的类型idref
    struct_offset, array_type_idref = get_variable_address_struct_array_offset(root, base_address, names[0], names[1],
                                                                               type_sizes)  # '0x8a:0x4bd31'
    array_var = ArrayVariable(var_name) #创建对象
    array_var.idref = array_type_idref

    die_name = get_variable_type_regular_array1(root, array_var) # 找到数组类型的名字：后面找不到数据类型大小，就用名字人为进行偏移
    if die_name is None:
        return None
    A = get_variable_type_regular_array_element_byte_size(root, array_var) #通过xml文件查找数组数据类型大小
    offset_address = array_var.calculate_offset_address(type_sizes,A) # 计算二维数组的偏移地址

    if offset_address is None:
        return None

    address = base_address + struct_offset + offset_address
    return address


def get_variable_address_array(root, var_name, type_sizes):
    if '.' in var_name:
        # Process array within a structure
        return get_variable_address_struct_array(root, var_name, type_sizes)
    else:
        # Process regular array
        return get_variable_address_regular_array(root, var_name, type_sizes)


def get_variable_address(root, var_name, type_sizes):
    if '[' in var_name:
        return get_variable_address_array(root, var_name, type_sizes)
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

    start_marker = "# 数据类型_开始行"
    end_marker = "# 数据类型_结束行"
    var_start_marker = "# 常用变量_开始行"
    var_end_marker = "# 常用变量_结束行"
    prefix_start_marker = "# 变量前缀_开始行"
    prefix_end_marker = "# 变量前缀_结束行"

    reading_sizes = False
    reading_vars = False
    reading_prefixes = False

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
                
                if reading_prefixes:
                    file_variables.append(line)

            # 如果文件中有数据，则使用文件中的数据
            if file_type_sizes:
                type_sizes = file_type_sizes
            if file_variables:
                variables = file_variables

    except Exception as e:
        print(f"加载type_sizes.txt时发生错误: {e}")
        #QMessageBox.warning(self, "警告", "加载type_sizes.txt时发生错误")
    return type_sizes, variables, common_variables  # 增加返回 common_variables




def convert_out_to_xml(ofd6x_path, out_file):
    xml_file = os.path.splitext(out_file)[0] + ".xml"
    cmd = f"{ofd6x_path} --xml --dwarf {out_file} > {xml_file}"

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"执行命令时发生错误: {e}")
        return None

    return xml_file


def parse_dwarf_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
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


class AddressFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.type_sizes, self.variables, self.common_variables = load_type_sizes(self)  # 获取常用变量
        self.initUI()
        self.previous_variables = [""] * 15

    def initUI(self):
        self.setWindowTitle("OUT文件取址工具")
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()  # 创建一个垂直布局管理器（QVBoxLayout），用于将窗口部件按照垂直方向排列。

        # Top info layout with author, version, and refresh button
        top_layout = QHBoxLayout()  # 创建一个水平布局管理器（QHBoxLayout），用于将窗口部件按照水平方向排列。

        info_layout = QVBoxLayout()  # 再次创建一个垂直布局管理器，用于在顶部信息布局下方添加额外的信息部件。
        self.company_version_label = QLabel("公司: Sineng  版本: 1.0.5 ")
        self.TODO_label = QLabel("TODO: 不支持二维数组以上的搜索;  局部刷新只会更新名称有变化的变量;")
        self.TODO_label1 = QLabel("系数   U16变量:0    电流:336     电网电压:690   母线电压:1200")
        info_layout.addWidget(self.company_version_label)
        info_layout.addWidget(self.TODO_label)
        info_layout.addWidget(self.TODO_label1)

        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_addresses)  # 刷新函数
        self.refresh_button.setFixedSize(80, 80)

        self.partial_refresh_button = QPushButton("局部刷新")
        self.partial_refresh_button.clicked.connect(self.partial_refresh_addresses)
        self.partial_refresh_button.setFixedSize(80, 80)
        
        self.refresh_xml_button = QPushButton("刷新XML文件")
        self.refresh_xml_button.clicked.connect(self.refresh_xml_file)
        self.refresh_xml_button.setFixedSize(120, 80)

        top_layout.addLayout(info_layout)
        top_layout.addStretch(1)
        top_layout.addWidget(self.refresh_button)
        top_layout.addWidget(self.partial_refresh_button)
        top_layout.addWidget(self.refresh_xml_button)

        layout.addLayout(top_layout)

        # ofd6x path input
        ofd6x_layout = QHBoxLayout()
        self.default_path_button = QPushButton("默认路径")
        self.default_path_button.clicked.connect(self.set_default_ofd6x_path)
        self.ofd6x_label = QLabel("ofd6x工具路径:")
        self.ofd6x_input = QLineEdit()
        self.ofd6x_browse = QPushButton("浏览")
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
        self.out_browse = QPushButton("浏览")
        self.out_browse.clicked.connect(self.browse_out)
        out_layout.addWidget(self.out_label)
        out_layout.addWidget(self.out_input)
        out_layout.addWidget(self.out_browse)
        layout.addLayout(out_layout)

        # XML update info output
        self.xml_update_label = QLabel("XML更新信息:")
        self.xml_update_output = QLineEdit()
        self.xml_update_output.setReadOnly(True)
        xml_update_layout = QHBoxLayout()
        xml_update_layout.addWidget(self.xml_update_label)
        xml_update_layout.addWidget(self.xml_update_output)
        layout.addLayout(xml_update_layout)

        # Variable names input
        self.var_labels = [QLabel(f"变量名称{i + 1}:") for i in range(15)]
        self.var_inputs = [QLineEdit() for _ in range(15)]
        self.addr_labels = [QLabel(f"MAP地址{i + 1}:") for i in range(15)]
        self.addr_outputs = [QLineEdit() for _ in range(15)]
        self.sn_addr_labels = [QLabel(f"上能地址{i + 1}:") for i in range(15)]
        self.sn_addr_outputs = [QLineEdit() for _ in range(15)]

        completer = QCompleter(self.variables)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        
        for i in range(15):
            var_layout = QHBoxLayout()
            self.var_inputs[i].setFixedWidth(400)  # Decrease variable input width
            self.var_inputs[i].setCompleter(completer)
            
            select_prefix_button = QPushButton("变量前缀")
            select_prefix_button.clicked.connect(lambda _, idx=i: self.show_variable_dialog(idx))

            select_common_var_button = QPushButton("常用变量")
            select_common_var_button.clicked.connect(lambda _, idx=i: self.show_common_variable_dialog(idx))

            self.addr_outputs[i].setFixedWidth(100)
            self.sn_addr_outputs[i].setFixedWidth(100)

            var_layout.addWidget(self.var_labels[i])
            var_layout.addWidget(self.var_inputs[i])
            var_layout.addWidget(select_prefix_button)
            var_layout.addWidget(select_common_var_button)
            var_layout.addWidget(self.addr_labels[i])
            var_layout.addWidget(self.addr_outputs[i])
            var_layout.addWidget(self.sn_addr_labels[i])
            var_layout.addWidget(self.sn_addr_outputs[i])
            self.addr_outputs[i].setReadOnly(True)
            self.sn_addr_outputs[i].setReadOnly(True)
            layout.addLayout(var_layout)

        self.setLayout(layout)

        # Automatically find ofd6x tool and out file if possible
        A = self.auto_find_tools()
        if(A != None):
            self.refresh_xml_file()

    def show_variable_dialog(self, idx):
        dialog = QDialog(self)
        dialog.setWindowTitle("选择变量前缀")
        layout = QVBoxLayout(dialog)

        var_list = QListWidget(dialog)
        for var in self.variables:
            item = QListWidgetItem(var)
            var_list.addItem(item)

        def on_var_selected():
            selected_items = var_list.selectedItems()
            if selected_items:
                self.var_inputs[idx].setText(selected_items[0].text())
            dialog.accept()

        var_list.itemDoubleClicked.connect(on_var_selected)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(on_var_selected)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(var_list)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

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
        path, _ = QFileDialog.getOpenFileName(self, "选择ofd6x工具路径")
        if path:
            self.ofd6x_input.setText(path)

    def browse_out(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择OUT文件路径")
        if path:
            self.out_input.setText(path)

    def refresh_addresses(self):
        dwarf_info = parse_dwarf_xml(self.xml_file)
        if dwarf_info is None:
            QMessageBox.warning(self, "错误", "解析XML文件失败")
            return
        for i in range(15):
            var_name = self.var_inputs[i].text().strip()
            if var_name:
                address = get_variable_address(dwarf_info, var_name, self.type_sizes)
                if address is not None:
                    self.addr_outputs[i].setText(hex(address))
                    sn_address = address - 0x8000
                    data2 = hex(sn_address)[2:] 
                    self.sn_addr_outputs[i].setText(data2)
                else:
                    self.addr_outputs[i].setText("未找到/数组地址越界")
                    self.sn_addr_outputs[i].setText("未找到/数组地址越界")
                self.previous_variables[i] = var_name


    def partial_refresh_addresses(self):
        dwarf_info = parse_dwarf_xml(self.xml_file)
        if dwarf_info is None:
            QMessageBox.warning(self, "错误", "解析XML文件失败")
            return
        for i in range(15):
            var_name = self.var_inputs[i].text().strip()
            if var_name != self.previous_variables[i]:
                address = get_variable_address(dwarf_info, var_name, self.type_sizes)
                if address is not None:
                    self.addr_outputs[i].setText(hex(address))
                    sn_address = address - 0x8000
                    data2 = hex(sn_address)[2:]
                    self.sn_addr_outputs[i].setText(data2)
                else:
                    self.addr_outputs[i].setText("未找到/数组地址越界")
                    self.sn_addr_outputs[i].setText("未找到/数组地址越界")
                self.previous_variables[i] = var_name

    def refresh_xml_file(self):
        ofd6x_path = self.ofd6x_input.text().strip()
        out_file = self.out_input.text().strip()
        self.xml_file = convert_out_to_xml(ofd6x_path, out_file)

        if self.xml_file:
            mod_time = time.ctime(os.path.getmtime(self.xml_file))
            self.xml_update_output.setText(f"最新修改日期: {mod_time}")
        else:
            QMessageBox.warning(self, "错误", "刷新XML文件失败")

    def set_default_ofd6x_path(self):
        current_dir = os.path.abspath(os.getcwd())
        ofd6x_path = find_file_in_directory(current_dir, "ofd6x.exe")
        if ofd6x_path:
            self.ofd6x_input.setText(ofd6x_path)
        else:
            QMessageBox.warning(self, "错误", "在当前路径下未找到 ofd6x.exe,")

    def auto_find_tools(self):
        # 获取当前工作目录的绝对路径
        current_directory = os.path.abspath(os.getcwd())

        # 查找当前目录下的 ofd6x.exe 文件
        ofd6x_files = [f for f in os.listdir(current_directory) if f == 'ofd6x.exe']
        if ofd6x_files:
            ofd6x_path = os.path.join(current_directory, ofd6x_files[0])
            self.ofd6x_input.setText(ofd6x_path)
        else:
            QMessageBox.warning(self, "警告", "当前路径下未找到 ofd6x.exe 文件")
            return None

        # 查找当前目录下的 .out 文件
        out_files = [f for f in os.listdir(current_directory) if f.endswith('.out')]
        if out_files:
            # 假设我们选择第一个找到的 .out 文件
            out_file_path = os.path.join(current_directory, out_files[0])
            self.out_input.setText(out_file_path)
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
    logging.debug('debug级别，一般用来打印一些调试信息，级别最低')    
    os.chdir(current_dir)
    app = QApplication(sys.argv)
    ex = AddressFinder()
    ex.show()
    sys.exit(app.exec())
