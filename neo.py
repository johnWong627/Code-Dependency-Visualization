import neo4j
import pyvis
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "12345678")


# file='/Applications/neo4j-community-5.9.0/bin'
"""



"""

def visualize_result(query_graph, nodes_text_properties):
    # visual_graph = pyvis.network.Network(select_menu=True, filter_menu=True)
    visual_graph = pyvis.network.Network(select_menu=True)
    # visual_graph =  pyvis.network.Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    # set the physics layout of the network
    # visual_graph.barnes_hut()

    visual_graph.show_buttons(filter_=['physics'])
    visual_graph.set_options("""
const options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -10300
    },
    "minVelocity": 0.75
  }
}
    """)


    for node in query_graph.nodes:
        node_label = list(node.labels)[0]
        node_text = node[nodes_text_properties[node_label]]
        visual_graph.add_node(node.element_id, node_text, group=node_label)  # todo id测试改为text，不行用text覆盖id前面内容

    for relationship in query_graph.relationships:
        visual_graph.add_edge(
            relationship.start_node.element_id,
            relationship.end_node.element_id,
            title=relationship.type,
            arrows="to"  # 并指定箭头的方向
        )
    visual_graph.toggle_physics(True)
    visual_graph.show('network.html', notebook=False)


def find_single_relationships(node_name, language):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            graph_result = driver.execute_query(
                f"match (n:{language} {{name:$node_name}})-[r:UPPER]->(m:{language}) return n,r,m",
                {'node_name': node_name}, result_transformer_=neo4j.Result.graph,
            )
            nodes_text_properties = {  # what property to use as text for each node
                language: "name"
            }
            visualize_result(graph_result, nodes_text_properties)

        except Exception as e:
            print(e)


def find_all_relationships(node_name, language, level, relation='UPP'):
    # match p=(n:python {name:'bs4'})-[r:UPP *]->(m:python) where  not (m)-[:UPP]->() return p
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            graph_result = driver.execute_query(
                f"match p=(n:{language} {{name:$node_name}})-[r:{relation} *1..{level}]->(m:python) where  not (m)-[:{relation}]->() return p",
                {'node_name': node_name}, result_transformer_=neo4j.Result.graph,
            )
            nodes_text_properties = {  # what property to use as text for each node
                language: "name"
            }
            visualize_result(graph_result, nodes_text_properties)

        except Exception as e:
            print(e)


# 检查节点的上层组件关系是否创建
def check_upper_relationship(language, node_name):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            res = driver.execute_query(f'match (n:{language} {{name:$node_name}}) return n.name',
                                       {'node_name': node_name}).records
            if len(res) == 0:
                return False
            else:
                res = driver.execute_query(
                    f"match (:{language}{{name:$node_name}})-[:UPP]->(end_nodes:{language}) return end_nodes.name",
                    {'node_name': node_name}).records
                if len(res) == 0:
                    return False
        except Exception as e:
            print(e)

    print(f"{node_name}：There already exists a upper level of relationship.")
    return True





def create_relationships(language, start_node, end_nodes):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            res, summary, keys = driver.execute_query(
                f'merge (start_node: {language} {{name:$start_node}}) with start_node '
                f'unwind {end_nodes} as en '
                f'merge (end_node:{language} {{name:en}}) '
                f'merge (start_node)-[:UPP]->(end_node)'
                f'merge (end_node)-[:LOW]->(start_node)',
                {"start_node": start_node})

        except Exception as e:
            print(e)


if __name__ == '__main__':
    # create_relationships(language, start_node, end_nodes)
    # res = find_single_relationships('bs4', language='python')
    print('开始')
    level = 3
    # find_all_relationships('bs4', language='python',level=level)
    find_all_relationships('flask', language='python',level=level)
    # find_all_relationships('io', language='python', relation='LOW', level=level)
    print('结束')

    # print(res)
