# Real-Time Flow Scheduling on P4

## Introcution 
P4(Programming Protocol-Independent Packet Processors) is a programmable language specifically designed for defining the data plane behavior of network devices. It allows users to customize and program the behavior of switches, providing flexibility to define how packets are processed, including specifying custom protocol fields,table entries and header.


We will use the following topology for the repo. ![pod-topo](./pod-topo.png)
 In this repo,each swtich has two flow tables, one is the forward flow table, and the other is the priority table.
```
sudo python3 network.py
```
This code helps to generate the network and topology. Afterward, you need to open send1.py or other send.py files depending on your need. 
```
sudo python3 send1.py duration.
```
Then you need to run controller. 
```
sudo controller.py
```
