BLOCK_SIZE = 4  # 真实ip个数
MUTATION_TIME = 5  # 突变时间设置
REAL_IPS = ['10.0.0.%s' % i for i in range(BLOCK_SIZE)]  # 真实地址池
VIRTUAL_IPS = ['10.0.0.%s' % i for i in range(BLOCK_SIZE, 3 * BLOCK_SIZE)]  # 虚拟地址池