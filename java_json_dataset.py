import json
import os

import pandas as pd


def java_get_pom_path():
    repository_path = '/Library/apache-maven-3.8.8/repository'
    list_pom = []
    for root, dirs, files in os.walk(repository_path):
        for file in files:
            if file.endswith('.pom'):
                list_pom.append(os.path.join(root, file))

    # 将list_pom写进txt文件,每个元素以回车隔开
    with open('java_list_pom.txt', 'w') as f:
        for item in list_pom:
            f.write("%s\n" % item)


def java_read_name():
    with open('/Users/john/IdeaProjects/test_maven/java_dependencies.json', 'r') as f:
        packages_dependencies = json.load(f)
        print(f'有{len(packages_dependencies)}个包被读取')
        dict_name = {}  # 包名重复检查

        for package in packages_dependencies:  # 遍历包
            # 打印字典package的所以键





            # print(package.getKeys())

            count = 0
            name = package['groupId'] + ' ' + package['artifactId']
            print(name)
            if dict_name.get(name) == None:
                dict_name[name] = package['managementKey']
            else:
                print('repeat', name, package['managementKey'])
            # print(type(package["dependencies"]))
            # dependency_count = len(package["dependencies"])  # 统计包的依赖包的数量


def java_read_data():
    pass


if __name__ == '__main__':
    # java_get_pom_path()
    # java_read_data()
    java_read_name()
