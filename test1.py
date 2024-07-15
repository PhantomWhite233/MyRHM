import networkx as nx
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from time import sleep


class MyTopo(Topo):
    # 需要注意这里设置的情况要和const中的一致
    def __init__(self):
        super(MyTopo, self).__init__()

        self.hosts = []
        self.switches = []
        self.links = []

        Host1 = self.addHost("h1", ip="10.0.0.1", mac="00:00:00:00:00:01")
        Host2 = self.addHost("h2", ip="10.0.0.2", mac="00:00:00:00:00:02")
        Host3 = self.addHost("h3", ip="10.0.0.3", mac="00:00:00:00:00:03")
        Host4 = self.addHost("h4", ip="10.0.0.4", mac="00:00:00:00:00:04")

        switch1 = self.addSwitch("s1")
        switch2 = self.addSwitch("s2")
        switch3 = self.addSwitch("s3")

        self.addLink(Host1, switch1, port1=1, port2=1)
        self.addLink(Host2, switch1, port1=1, port2=2)
        self.addLink(Host3, switch2, port1=1, port2=1)
        self.addLink(Host4, switch3, port1=1, port2=1)

        self.addLink(switch1, switch2, port1=10, port2=11)
        self.addLink(switch2, switch3, port1=12, port2=13)


def create_networkx_graph():
    G = nx.Graph()

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

    return G


def main():
    mytopo = MyTopo()

    # 创建拓扑图
    G = create_networkx_graph()
    nx.write_gml(G, "MyTopo.gml")
    
    # # 创建mininet网络
    # net = Mininet(
    #     topo=mytopo, link=TCLink, controller=RemoteController("c", "127.0.0.1", 6633)
    # )

    # net.start()
    # sleep(5)
    # # net.pingAll()

    # CLI(net)

    # net.stop()


# topos = {"mytopo": lambda: MyTopo()}

if __name__ == "__main__":
    main()
