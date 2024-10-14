# Real-Time Flow Scheduling on P4

## Introcution 
P4(Programming Protocol-Independent Packet Processors) is a programmable language specifically designed for defining the data plane behavior of network devices. It allows users to customize and program the behavior of switches, providing flexibility to define how packets are processed, including specifying custom protocol fields,table entries and header.


We will use the following topology for the repo. [topol.pdf](./topol.pdf).
In this repo,each swtich has two flow tables, one is the forward flow table, and the other is the priority table. Additionally, there is a custom header and parser can extract the necessary data that can be utilized in the flow table. We will evaluate the performance of the two scheduling algorithms 


## Step 1: Run the Mininet

To run the script, you first need to run the Mininet environment using the following command.
```
sudo python3 network.py
```
This will:
* configure all hosts and switchs listed in `topol.pdf` file. 
* start the topol in Mininet and configure all swtiches with the P4 program and table entries.
  
The links and port of network are configured in the `s1-commands`,`network.py` and `s2-commands` files. The specific configuration is as follows:
```
table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.6/32 => 00:00:0a:00:01:06 4
table_add MyIngress.ipv4_lpm ipv4_forward 10.0.2.3/32 => 00:00:0a:00:02:00 8
```
## Step 2: Send the flow

Instead of using iperf, threads are a better option for creating custom flows. In tis repo,each real time flow contains `deadline`, `weight` and `flow id`. The `dedline` and `weight` are used by different algorithm,while the `flow id` is used to determine the exact flow. 
To send the flow, you need to using the following command.
```
sudo python3 send1.py duration
```
The `duration` represents the time period. You can modify the duration the flow speed to  manipulate the network environemnt based on the test requirement. Also, you are free to compile the data types contained in the floww, but all data must be intergers. For example, if it's `relative time` of packet sending(which is float), it must be converted to an integer before sending.

## Step 3: Run the controller
In this repo, there are two controllers, and each can be run using its respective command.
```
sudo python3 controller.py
sudo python3 controller1.py
```
Each controller use a different scheduling algorithm. Our slack monotnoic algorithm is applied in `controller.py`, while the shortest finish time first algorithm is applied in `controller1.py`.

## Thrift API and Communication 
Nowadays, controller more commonly use the Thrift API and P4Runtime API to communicate with switches.We used register,corresponding register helper functions, and flow tables provided by Thrift API to communicate with switch and transfer data. In addition to these two API's, the P4 community also provides some helper files to assist controller. These API and files are written in the `P4-utils` file.
On the other hand, you can also compile and modify the Thrift API as needed. For example, we avoid table duplication by check whether the following variables are equal in this repo.
```
if(entry.mtach_key[0].exact.keys == match_key[0].exact.keys)
```
