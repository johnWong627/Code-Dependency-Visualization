import os
import ast  # python解析
import javalang  # 针对JDK8
import plyj.parser as plyj  # 该解析器课只支持JDK7,做为第二解析，并且可以指出具体哪一行有语法错误（语法要求较高，如多一个；也不行）
import re

import neo

# 匹配多行注释，即/*(文本包含内容)*/
pattern1 = r"/\*.*?\*/"
# 匹配单行注释，即//(文本包含内容)
pattern2 = r"//.*"
# 匹配#include<内容.h> 或#include "内容.h" 中的内容
pattern_angle = r"#include *<.+"
pattern_quotation = r"#include *\".+"
# todo .lib或.dll文件
"""
说明：不能检测出语法错误,
如果在printf或std::cout中的字符串中有pattern_angle或pattern_quotation匹配的模型，则亦会被提取
"""


# 定义一个函数，用于提取文本中的包含内容
def c_extract_includes(text) -> list:
    # 去掉文本中的注释部分
    # 使用sub函数，将匹配到的多行注释替换为空字符串
    text = re.sub(pattern1, "", text, flags=re.DOTALL)
    # 使用sub函数，将匹配到的单行注释替换为空字符串
    text = re.sub(pattern2, "", text)
    # print(text)
    # 使用findall函数，返回一个列表，包含所有匹配到的提取内容
    includes_angel = re.findall(pattern_angle, text)
    includes = re.findall(pattern_quotation, text)
    includes_angel = [i.split('<')[1].split('>')[0].split('.')[0] for i in includes_angel]
    includes = [i.split('"')[1].split('.')[0] for i in includes]
    includes.extend(includes_angel)
    return includes

# todo c_plus 改成cpp
def parse_library(library_path, current_library=None, language=None, check_upper_relationship=True):
    if current_library is None:
        current_library = library_path.split('/')[-1]
    filter_set = set()
    is_library = False
    all_file = []
    java_precision = 3  # 包路径的保存精度
    # 通过判断该项目的文件夹中的文件的后缀来判断该项目的language
    for root, dirs, files in os.walk(library_path):
        if language is not None:
            break
        for file in files:
            if file.endswith('.java'):
                language = 'java'
                break
            if file.endswith('.py'):
                language = 'python'
                break
            if file.endswith('.cpp') or file.endswith('.cxx') or file.endswith('.c') or file.endswith('.cc'):
                language = 'c'
                break

    if language is None:
        # print('文件夹没有能解析的代码文件，仅支持python,java,c,c++')
        return False,language
    # 找到library_path路径下所有后缀为py的文件,加到filter_set
    if language == 'python':
        if check_upper_relationship and neo.check_upper_relationship(language,
                                                                     current_library): return False,language  # 检查current_library是否有上层组件
        filter_set.add(current_library)
        for root, dirs, files in os.walk(library_path):
            if '__init__.py' in files:
                if not is_library:
                    is_library = True
                self_package = root.split('/')[-1]  # 本项目的函数
                filter_set.add(self_package)

            if '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    all_file.append(os.path.join(root, file))
                    file = file[:-3]  # 去掉 py的后缀
                    filter_set.add(file)
        if not is_library:
            if current_library.endswith('-info'): return False,language
            print(f'<{current_library}> 无__init__.py文件，可能为非库函数或无上层组件')

        print(f'{current_library}包含{len(all_file)}个{language}文件')
        upper_set = set()
        for single_file in all_file:
            with open(single_file, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
                try:
                    tree = ast.parse(code)
                    # print(ast.dump(tree, indent=4))
                except Exception as e:
                    print(f'文件可能存在语法错误，不能解析：{single_file}')
                    print('语法错误信息：', e)
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            node_name = alias.name.split('.')[0]
                            if current_library == node_name:
                                continue
                            upper_set.add(node_name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module is None:
                            continue
                        node_name = node.module.split('.')[0]
                        if current_library == node_name:
                            continue
                        upper_set.add(node_name)
        upper_set = upper_set.difference(filter_set)
        end_nodes = [element for element in upper_set if element != '']
        # print(f' {len(end_nodes)}个上层组件')
        if len(end_nodes) == 0: return False,language
        neo.create_relationships(language, current_library, end_nodes)
        return True,language
    elif language == 'java':  # todo 多个库函数测试 ，import下置测试
        check_parser = plyj.Parser()
        start_node_dict = {}
        file_sum = 0  # 扫描文件数
        wrong_sum = 0  # 疑似语法文件数
        for root, dirs, files in os.walk(library_path):
            # if 'test' in root: continue # test jdk1.8 source code
            for file in files:
                if file.endswith('.java'):
                    file_sum += 1
                    java_path = os.path.join(root, file)
                    with open(java_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                        try:
                            tree = javalang.parse.parse(code)
                            package = tree.package
                            if package is None:
                                continue
                            package = package.name
                            imports = tree.imports
                            imports = [item.path for item in imports]

                        except Exception as e:
                            tree = check_parser.parse_string(code)
                            if tree is None:
                                print(f'文件可能存在语法错误，不能解析：{java_path}')
                                wrong_sum += 1
                                continue
                            package = tree.package_declaration
                            if package is None:
                                continue
                            package = package.name.value
                            imports = tree.import_declarations
                            imports = [item.name.value for item in imports]
                        package = '.'.join(package.split('.')[:java_precision])
                        # 将package作为start_node_dict的键，值为set数据类型
                        if package not in start_node_dict:
                            start_node_dict[package] = set()

                        for node in imports:
                            # 切掉 node中第一个大写字母后面的内容（包括第一个大写字母和前面的.）
                            cut_point = re.search('.[A-Z]', node)
                            if cut_point != None:
                                node = node[:cut_point.start()]
                            # node以.划分个数取前3个(java_precision=3)，不够3个取全部，如‘tk.mybatis.spring.annotation.MapperScan’变成‘tk.mybatis.spring’
                            node = '.'.join(node.split('.')[:java_precision])
                            start_node_dict[package].add(node)
        print(f'疑似语法文件占比：{wrong_sum / file_sum:.4f}，文件总数：{file_sum}，错误文件数：{wrong_sum}')
        # 将start_node_dict的键放进filter_set
        filter_set = filter_set.union(start_node_dict.keys())  # 并集

        # 将start_node_dict中每个值的set与filter_set做差集，将结果放置地start_node_dict中
        for key, value in start_node_dict.items():
            if len(value) != 0:
                start_node_dict[key] = value.difference(filter_set)
                # print(f'write {len(value)}nodes',end=' ')
                neo.create_relationships(language, key, list(start_node_dict[key]))  # 写入数据库
        # 打印start_node_dict的键和对应的值
        count = 0
        for key, value in start_node_dict.items():
            len_value = len(value)
            if len_value == 0:
                continue
            print('---')
            print(key, len_value, end=' ')
            count += len_value
            print(':')
            for item in value:
                print(item)
        print('共有组件：', len(start_node_dict))
        print('共有关系', count)
        return True,language
    elif language == 'c':
        c_includes = set()
        c_plus_project = False
        for root, dirs, files in os.walk(library_path):
            for file in files:
                # print(os.path.join(root, file))
                if file.endswith('.c'):
                    c_path = os.path.join(root, file)
                    with open(c_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                        c_includes = c_includes.union(c_extract_includes(code))
                elif file.endswith('.cpp') or file.endswith('.cxx') or file.endswith('.cc'):  # 把.cc后缀视为c++文件
                    if not c_plus_project: c_plus_project = True
                    c_path = os.path.join(root, file)
                    with open(c_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                        c_includes = c_includes.union(c_extract_includes(code))
                elif file.endswith('.h') or file.endswith('.hpp'):  # todo 不考虑不把第三方库引入项目文件夹的情况
                    filter_set.add(file.split('.')[0])
                    c_path = os.path.join(root, file)
                    with open(c_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                        c_includes = c_includes.union(c_extract_includes(code))
        if c_plus_project:
            language = 'cpp'
        else:
            language = 'c'
        c_includes = c_includes.difference(filter_set)
        neo.create_relationships(language, current_library, list(c_includes))
        return True,language


if __name__ == '__main__':
    # todo github项目集测试
    python_path = '/Users/john/miniforge3/envs/pytorch/lib/python3.10'
    libraries = '/Users/john/miniforge3/envs/pytorch/lib/python3.10/site-packages'
    # python_single_file = '/Users/john/miniforge3/envs/pytorch/lib/python3.10/site-packages/bs4'
    # python_single_file='/Users/john/miniforge3/envs/pytorch/lib/python3.10/site-packages/neo4j'
    # java_single_library = '/Users/john/java_projects/ApplianceMall'
    # java_single_library = '/Users/john/jdk1.8/openjdk'
    c_single_file = '/Users/john/test_code/GreedySnake'
    # python_single_file = '/Users/john/test_code/python_project'
    # test
    # java_single_library = '/Users/john/jdk1.8/openjdk/jdk/test/jdk/lambda'
    # java_single_library = '/Users/john/jdk1.8/openjdk/jaxws/src/share/jaxws_classes/javax/jws'
    # java_single_library = '/Users/john/jdk1.8/openjdk/jaxws/src/share/jaxws_classes/javax/jws/soap'
    # library_path = '/Users/john/miniforge3/envs/pytorch/lib/python3.10/site-packages/torch'
    # parse_library(library_path)
    libraries = [os.path.join(libraries, item) for item in os.listdir(libraries)]  # 多个库函数
    libraries = [item for item in libraries if os.path.isdir(item)]  # 去文件
    lib_count = 0
    # parse_library(java_single_library)
    # parse_library(c_single_file)
    # parse_library(python_single_file)
    # 遍历python库
    for library_path in libraries:
        # print(library_path)
        if parse_library(library_path, check_upper_relationship=False): lib_count += 1
        # if lib_count == 10: break

    # parse_library(python_single_file)
    print(f'有{lib_count}个库函数')
    print()
    print('全部文件解析完毕')
