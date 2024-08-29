import pandas as pd

path='/Users/john/Downloads/Libraries.io-open-data-1.0.0'
# file='dependencies-1.0.0-2017-06-15.csv'
# file='projects_with_repository_fields-1.0.0-2017-06-15.csv'
# file='projects-1.0.0-2017-06-15.csv'
file='repositories-1.0.0-2017-06-15.csv'
file='repository_dependencies-1.0.0-2017-06-15.csv'
file='tags-1.0.0-2017-06-15.csv'
file='versions-1.0.0-2017-06-15.csv'
# 设置display.max_columns参数为None，以显示所有列
pd.set_option('display.max_columns', None)
file=path+'/'+file
# 读文件前5行，并且显示每一列的显示不省略
df = pd.read_csv(file, nrows=100, encoding='utf-8')
#打印每一列的名称，用逗号隔开
print(df.columns.values)
# print(df)
#指定显示第10行到20行
print(df.iloc[89:93, :])