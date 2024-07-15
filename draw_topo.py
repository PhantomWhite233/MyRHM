import networkx as nx
import matplotlib.pyplot as plt

# 读取GML文件生成NetworkX图
G = nx.read_gml('network_5.gml')

# 打印节点和边的数量
print('Total Number of Nodes:', len(G.nodes))
print('Total Number of Edges:', len(G.edges))

# 创建节点颜色和标签映射
node_colors = []
node_labels = {}
for node, data in G.nodes(data=True):
    if data['type'] == 'host':
        node_colors.append('lightgreen')  # 主机节点为蓝色
    else:
        node_colors.append('red')  # 交换机节点为红色
    node_labels[node] = node

# 绘制图形
pos = nx.spring_layout(G)  # 使用弹簧布局

plt.figure(figsize=(12, 8))

# 绘制节点
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)

# 绘制边
nx.draw_networkx_edges(G, pos)

# 绘制标签
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12)

# 显示图形
plt.title('Network Topology')
plt.show()
