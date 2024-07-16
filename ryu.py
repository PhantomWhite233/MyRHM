import random
import networkx as nx
import const
from copy import deepcopy
from threading import Timer
from ryu.topology import event
from ryu.base import app_manager
from collections import defaultdict
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3
from ryu.topology.api import get_switch, get_link
from ryu.lib.packet import packet, ethernet, arp, lldp, ipv4, ipv6, ether_types, icmp
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER


class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)

        self.real_ips = deepcopy(const.REAL_IPS)  # 真实ip地址池
        self.virtual_ips = deepcopy(const.VIRTUAL_IPS)  # 虚拟ip地址池

        self.datapaths = {}  # 管理的所有交换机
        self.real2virtual = {}  # 真实地址到虚拟地址的映射
        self.virtual2real = {}  # 虚拟地址到真实地址的映射
        self.real2host = {}  # 真实ip和主机的映射
        
        self.graph = nx.read_gml('MyTopo.gml')  # 读取网络拓扑结构
        self.paths = defaultdict(lambda: defaultdict(list))  # 存储原地址到目的地址的路径
        
        
        # 测试用：真实ip和虚拟ip的映射
        for i in range(4):
            real_ip = self.real_ips[i]
            virtual_ip = self.virtual_ips[i]
            self.real2virtual[real_ip] = virtual_ip
            self.virtual2real[virtual_ip] = real_ip

        print("real to virtual:")
        print(self.real2virtual)
        print("virtual to real:")
        print(self.virtual2real)

        # 测试用：初始化ip到host的映射
        for node, data in self.graph.nodes(data=True):
            if node[0] == 'h':
                self.real2host[data["ip"]] = node

    # 函数意义：
    #       清空对应交换机流表
    # 参数说明：
    #       datapath-Openflow交换机对象，需要清空他的流表项
    def empty_flow_table(self, datapath):
        print('Empty Flow Table')
        ofproto = datapath.ofproto  # 协议对象，包含Openflow协议常量，例如动作类型等信息
        parser = datapath.ofproto_parser  # 解析器对象，包含创建Openflow信息的方式

        match = parser.OFPMatch(in_port=1)  # 创建一个匹配对象，指定匹配条件为输入端口1
        # 创建一个流表修改信息对象，此处为删除流表项信息
        mod = parser.OFPFlowMod(datapath, cookie=0, cookie_mask=0, table_id=0, command=ofproto.OFPFC_DELETE, idle_timeout=0, hard_timeout=0, priority=1, 
                                buffer_id=ofproto.OFPCML_NO_BUFFER,out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY, flags=0, match=match, instructions=[])

        datapath.send_msg(mod)  # 发送删除流表项信息

    # 函数意义：
    #       当交换机接收到一个没有匹配流表项的数据包，会触发table-missing flow entry流表项，
    #       然后会将这个数据包发送到控制器
    # 参数说明：
    #       datapath-Openflow交换机对象，需要对其添加table-miss流表项
    def missing_flow_table(self, datapath):
        print('Missing Flow Table')
        ofproto = datapath.ofproto  # 协议对象
        parser = datapath.ofproto_parser  # 解析器对象

        match = parser.OFPMatch()  # 创建一个匹配对象，匹配所有数据包
        # 创建一个动作对象，此处为将数据包发送到控制器的动作
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        self.add_flow(datapath, 0, match, actions)  # 向交换机添加流表项，优先级最低

    # 函数意义：
    #       添加流表项
    # 参数说明：
    #       datapath-Openflow交换机对象
    #       priority-流表项的优先级
    #       match-流表项的匹配条件
    #       actions-当数据包匹配流表项时要执行的动作列表
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto  # 协议对象
        parser = datapath.ofproto_parser  # 解析器对象

        # 创建一个应用动作的指令对象
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        # 创建流表修改信息
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)

        datapath.send_msg(mod)  # 发送流表修改信息

    # 函数意义：
    #       计算路径
    # 参数说明：
    #       src-源节点
    #       dst-目的节点
    def get_path(self, src, dst):
        # 检查路径是否已经存储，若未存储才进行计算
        if len(self.paths[src][dst]) == 0:
            self.paths[src][dst] = nx.shortest_path(self.graph, src, dst) # 直接调用networkx中函数计算最短路径

        # print('shortPath: %s -> %s: %s' % (src, dst, self.paths[src][dst]))
        return self.paths[src][dst]
    
    # 函数意义：
    #       计算
    def is_connect(self, u, v):
        if not self.edges[u][v]:
            self.edges[u][v] = self.graph.has_edge(u, v)

    # 触发时机：
    #       在交换机和控制器完成握手时触发，此时控制器正处于配置交换机状态
    # 函数意义：
    #       用于处理Openflow交换机特性事件
    #       一般来说这个函数是用来初始化配置Openflow交换机的
    # 参数说明：
    #       ev-事件对象
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg  # 从事件对象中提取消息
        datapath = msg.datapath  # 从消息中提取Openflow交换机对象
        self.datapaths[datapath.id] = datapath  # 存储所发现的交换机对象

        self.missing_flow_table(datapath)  # 一般在握手完成后控制器将table-missing flow entry添加到流表中

    # 触发时机：
    #       在EventOFPPacketIn事件发生时，即当一个Openflow交换机收到一个数据包且没有匹配的流表项时，它会将该数据包发送到控制器时
    #       此时控制器正处于MAIN_DISPATCHER状态下，即交换机与控制器的连接已完全建立，控制器可以对交换机进行正常的控制和管理操作时
    # 函数意义：
    #       用于处理Openflow交换机特性事件
    # 参数说明：
    #       ev-事件对象
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # 初始化信息
        msg = ev.msg  # 提取信息
        datapath = msg.datapath  # 提取交换机对象
        dpid = 's%s' % datapath.id  # 得到交换机id
        ofproto = datapath.ofproto  # 协议对象
        parser = datapath.ofproto_parser  # 解析器对象
        in_port = msg.match['in_port']  # 消息来的交换机的端口，即数据包进入交换机的端口

        print("This is %s" %dpid)

        # 解析数据包，提取ARP、IPv4、IPv6、LLDP、ICMP、Ethernet协议的数据包
        pkt = packet.Packet(msg.data)
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        ipv6_pkt = pkt.get_protocol(ipv6.ipv6)
        lldp_pkt = pkt.get_protocol(lldp.lldp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        # 初始化动作列表
        actions = []

        # 忽略LLDP和IPv6数据包
        if lldp_pkt:
            return
        if ipv6_pkt:
            return
        
        # # 处理ICMP数据包
        # if icmp_pkt:
        #     # 制定icmp信息类型：0-Echo Reply (ping reply)，3-Destination Unreachable，
        #     #                  8-Echo Request (ping request)，11-Time Exceeded
        #     icmp_type = icmp_pkt.type_
        #     # 对于Echo Reply和Echo Request信息，都会包含一个echo对象，
        #     # 这个对象会有以下属性：
        #     #   id_ - 标识符，用于匹配 Echo Request 和 Echo Reply
        #     #   seq - 序列号，用于匹配请求和回复
        #     #   data - 实际的负载数据。
        #     icmp_data = icmp_pkt.data

        #     print("type:", icmp_type)
        #     print("data:", icmp_data)

        # 处理ARP数据包
        if arp_pkt:
            # 提取ARP包信息
            arp_src = arp_pkt.src_ip
            arp_dst = arp_pkt.dst_ip
            print("This is ARP")
            print("src:", arp_src, " dst:", arp_pkt)

            # 获取路径
            path = self.get_path(self.real2host[arp_src], self.real2host[arp_dst])
            print("Get path:", path)
            
            # 确定当前交换机在路径中的位置并找到下一跳
            if dpid in path:
                index = path.index(dpid)  # 获取当前交换机在路径中的位置索引
                next_hop = path[path.index(dpid) + 1]  # 下一跳
                out_port = self.graph[dpid][next_hop]['port']  # 获取去往下一跳交换机的本交换机端口号
                print('ARP Packet %s -> %s : port %s' % (path[index], path[index + 1], out_port))

                actions.append(parser.OFPActionOutput(out_port))  # 根据上述获得信息创建动作对象

                match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP,
                                        arp_spa=arp_src, arp_tpa=arp_dst)  # 创建一个匹配条件，匹配 ARP 包的以太网类型、源 IP 和目的 IP

                self.add_flow(datapath, 1, match, actions)  # 添加流表项

        # 处理ipv4数据包
        if ipv4_pkt:
            # 提取数据包发送方和接收方ip地址
            ipv4_src = ipv4_pkt.src
            ipv4_dst = ipv4_pkt.dst

            print("This is ipv4")
            print("src:", ipv4_src, " dst:", ipv4_dst)

            # 先进行真实ip和虚拟ip的转化
            # 获取整个路径
            path = self.get_path(self.real2host[ipv4_src], self.real2host[ipv4_dst])
            path_length = len(path)
            cur_index = path.index(dpid)
            print("path_length: %s. cur_index: %s" %(path_length, cur_index))
            # 如果是路径上第一个交换机，此时一定是真实ip，所以做真实ip向虚拟ip的转化
            if cur_index == 1:
                actions.append(parser.OFPActionSetField(ipv4_src=self.real2virtual[ipv4_src]))   # 修改表头参数
                actions.append(parser.OFPActionSetField(ipv4_dst=self.real2virtual[ipv4_dst]))
                print('Change SRC: %s(Real) -> %s(Virtual)' % (ipv4_src, self.real2virtual[ipv4_src]))
                print('Change DST: %s(Real) -> %s(Virtual)' % (ipv4_dst, self.real2virtual[ipv4_dst]))
            # 如果是路径上最后一个交换机，此时一定是虚拟ip，所以做虚拟ip向真实ip的转化
            if cur_index == path_length - 2:
                actions.append(parser.OFPActionSetField(ipv4_src=self.virtual2real[ipv4_src]))
                actions.append(parser.OFPActionSetField(ipv4_dst=self.virtual2real[ipv4_dst]))
                print('Change SRC: %s(Virtual) -> %s(Real)' % (ipv4_src, self.real_to_virtual[ipv4_src]))
                print('Change DST: %s(Virtual) -> %s(Real)' % (ipv4_dst, self.real_to_virtual[ipv4_dst]))

            # 然后进行转发工作的安排
            # 先将ip锁定为真实ip
            real_src = ipv4_src
            real_dst = ipv4_dst
            if ipv4_src in self.virtual_ip:
                real_src = self.virtual_to_real[ipv4_src]
            if ipv4_dst in self.virtual_ip:
                real_dst = self.virtual_to_real[ipv4_dst]
            # 然后查找下一跳和跳出端口
            next_hop = path[path.index(dpid) + 1]
            out_port = self.graph[dpid][next_hop]['port']
            print('Next Hop: %s, Out Port: %s' % (next_hop, out_port))
            actions.append(parser.OFPActionOutput(out_port))

        #  最终发送PacketOut信息，将数据包转发出去
        data = None
        # 若数据包不在交换机的缓冲区中，则将数据包写入data变量中
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        # 创建PacketOut信息，并发送
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

        # 清空流表
        self.empty_flow_table(datapath)
