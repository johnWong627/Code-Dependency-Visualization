import subprocess
import json

"""
要求安装pipdeptree库
说明：
1.使用pip库获取指定包的依赖包的信息，指定包的信息比较全，但不能像pipdeptree库获取依赖包的具体版本信息
"""


def get_python_dependencies_by_command(package_names):
    output=[]
    sep=16 # 命令行一次读取参数个数有限制
    # 使用 subprocess 模块来执行命令行 pipdeptree，并获取其输出
    # 将package_names以每组sep个为一个list，生成新的list
    package_names = [package_names[i:i+sep] for i in range(0, len(package_names), sep)]

    for package_name in package_names:
        package_dependencies=subprocess.check_output(["pipdeptree", "--json-tree", "-p", ','.join(package_name)])
        package_dependencies = json.loads(package_dependencies)
        output.extend(package_dependencies)
        # print(len(output))
    return output


def get_python_package_dependencies_data(package_names):
    json_data = get_python_dependencies_by_command(package_names)
    # 将json_data转化成数据文件
    # print(f'有{len(json_data)}个 package 被读取')
    with open('python_package_dependencies.json', 'w') as f:
        json.dump(json_data, f, indent=4, sort_keys=False)


def read_python_file():
    with open('python_package_dependencies.json', 'r') as f:
        packages_dependencies = json.load(f)
        print(f'有{len(packages_dependencies)}个包被读取')
        set_packages_name = set()
        for package in packages_dependencies: #遍历包
            count = 0
            print(package['package_name'])
            set_packages_name.add(package['package_name'])
            # print(type(package["dependencies"]))
            dependency_count=len(package["dependencies"]) # 统计包的依赖包的数量
            if dependency_count==0:
                # print(package['package_name'])
                print(dependency_count)
                continue
            set_package=set()
            for dependency in package["dependencies"]: # 遍历包的依赖包
                print(dependency["package_name"], end=' ')
                set_package.add(dependency["package_name"])
                count+=1
            print(count)
            if dependency_count != len(set_package):
                '该包的依赖有同名包'
    return set_packages_name

if __name__ == '__main__':
    # 备选 selenium matplotlib
    py_package_str = "wxPython seaborn plotly celery Faker gunicorn Scrapy Theano bokeh pyephem vosk transformers sacremoses torchmetrics pytest torchaudio tensorflow nltk moviepy numba pyinstaller boto3 dash streamlit jupyter"
    package_names = py_package_str.split()
    print('输入包数量',len(package_names))
    if len(package_names) != len(set(package_names)):
        print('存在同名包')
    # print(len(package_names))
    # package_names=['numpy']
    # data = get_python_dependencies_by_command(package_names)
    # print(data)
    get_python_package_dependencies_data(package_names)
    set_packages_name=read_python_file()
    # print(set_packages_name.difference(set(package_names)))
    # print(set(package_names))
    # print('package_names',set(package_names))
    # print('set_packages_name',set_packages_name)
    set_packages_name=set(package_names).difference(set_packages_name)
    print('输入中没有被读取的：',set_packages_name)
