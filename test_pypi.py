

# 导入requests库
import requests

# 指定要查询的包名，例如numpy
package_name = 'torch'

# 构建请求URL
url = f'https://pypi.org/pypi/{package_name}/json'

# 发送GET请求
response = requests.get(url)

# 检查响应状态码
if response.status_code == 200:
    # 解析响应内容为JSON对象
    data = response.json()
    print(data)
    # 获取元数据中的requires_dist字段，这个字段可能包含一些依赖信息
    requires_dist = data['info']['requires_dist']
    # 打印依赖信息，如果没有则打印None
    print(requires_dist or None)
else:
    # 打印错误信息
    print(f'Error: {response.status_code}')
