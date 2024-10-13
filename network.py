from p4utils.mininetlib.network_API import NetworkAPI

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.enableCli()

# Network definition
net.addP4Switch('s1', cli_input='s1-commands.txt')
# can also bee added as a parametter in addP4Switch
net.setPriorityQueueNum('s1', 8)
net.setP4Source('s1','multiqueueing.p4')

net.addP4Switch('s2', cli_input='s2-commands.txt')
# can also bee added as a parametter in addP4Switch
net.setPriorityQueueNum('s2', 8)
net.setP4Source('s2','multiqueueing.p4')

net.addHost('h1')
net.addHost('h2')
net.addHost('h3')
net.addHost('h4')
net.addHost('h5')
net.addHost('h6')
net.addHost('h7')
net.addHost('h8')
net.addHost('h9')
net.addLink('h1', 's1')
net.addLink('h2', 's1')
net.addLink('h5', 's1')
net.addLink('h7', 's1')
net.addLink('h6', 's1')
net.addLink('h8', 's1')
net.addLink('h9', 's1')

net.addLink('s1', 's2', bw=5)
net.addLink('s2', 'h3')
net.addLink('s2', 'h4')

# Assignment strategy
net.mixed()

# Nodes general options
net.enablePcapDumpAll()
net.enableLogAll()

# Start network
net.startNetwork()
