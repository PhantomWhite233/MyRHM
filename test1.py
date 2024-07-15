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

        self.hosts.extend([Host1, Host2, Host3, Host4])
        self.switches.extend([switch1, switch2, switch3])
        self.links.extend(
            [
                (Host1, switch1),
                (Host2, switch1),
                (Host3, switch2),
                (Host4, switch3),
                (switch1, switch2),
                (switch2, switch3),
            ]
        )


def create_networkx_graph(topo):
    G = nx.Graph()

    for host in topo.hosts:
        G.add_node(host, type="host")
    for switch in topo.switches:
        G.add_node(switch, type="switch")
    for link in topo.links:
        G.add_edge(*link)

    return G


def main():
    mytopo = MyTopo()

    # 创建拓扑图
    G = create_networkx_graph(mytopo)
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
