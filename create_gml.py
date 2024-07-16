import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

# 主机
for i in range(1,5):
    G.add_node(f"h{i}", ip=f"10.0.0.{i}", mac=f"00:00:00:00:00:0{i}")
# 交换机
for i in range(1, 4):
    G.add_node(f"s{i}")
# 链接
G.add_edge("h1", "s1", port=1)
G.add_edge("h2", "s1", port=1)
G.add_edge("h3", "s2", port=1)
G.add_edge("h4", "s3", port=1)
G.add_edge("s1", "h1", port=1)
G.add_edge("s1", "h2", port=2)
G.add_edge("s1", "s2", port=10)
G.add_edge("s2", "s1", port=11)
G.add_edge("s2", "h3", port=1)
G.add_edge("s2", "s3", port=12)
G.add_edge("s3", "s2", port=13)
G.add_edge("s3", "h4", port=1)

nx.write_gml(G, "MyTopo.gml")