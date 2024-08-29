
# 导入re库
import re




# 匹配多行注释，即/*(文本包含内容)*/
pattern1 = r"/\*.*?\*/"
# 匹配单行注释，即//(文本包含内容)
pattern2 = r"//.*"
# 匹配#include<内容.h> 或#include "内容.h" 中的内容
pattern_angle = r"#include *<.+"
pattern_quotation = r"#include *\".+"
#todo .lib或.dll文件
"""
说明：不能检测出语法错误,
如果在printf或std::cout中的字符串中有pattern_angle或pattern_quotation匹配的模型，则亦会被提取
"""

# 定义一个函数，用于提取文本中的包含内容
def c_extract_includes(text):
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
    print(type(includes[0]))
    includes.extend(includes_angel)
    # 返回提取内容的列表
    return includes


if __name__ == '__main__':
    path = '/Users/john/test_code'
    file = 'my.c'
    file = 'main.c'
    c_path = path + '/' + file

    with open(c_path, 'r') as f:
        code = f.read()
        res = c_extract_includes(code)
        print(res)
        # print(res)
