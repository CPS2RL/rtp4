import nnpy
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from scapy.all import sniff, Packet
import sys
import struct
import os
from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption, Ether, IP, raw
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.layers.inet import _IPOption_HDR
import time
import multiprocessing
import random
import time
import threading
from scapy.all import Ether, IP, UDP, Raw, sendp




class Controller(object):

    def __init__(self, sw_name):
        self.topo = load_topo('topology.json')
        self.sw_name = sw_name
        self.thrift_port = self.topo.get_thrift_port(sw_name)
        self.controller = SimpleSwitchThriftAPI(self.thrift_port)


    def _set_queue_rate(self, rate, port, priority):
        self.controller.set_queue_rate(rate, port, priority)
    def register_read(self, register_name, index):
        return self.controller.register_read(register_name, index)
    def table_dump(self, table_name):
        return self.controller.table_dump(table_name)
    def table_dump_keys(self, table_name,matches):
            return self.controller.table_dump_entry_from_key(table_name,matches)
    def table_add(self, table_name,actions,match_key,action_params=[]):
        return self.controller.table_add(table_name,actions,match_key,action_params)
    def table_modify_match(self, table_name, action_name, match_keys, action_params=[]):
        return self.controller.table_modify_match(table_name, actions, match_key,action_params)
    def table_action(self, table_name):
        return self.controller.dump_action_entry(table_name);
    def table_entry(self, table_name,entry):
        return self.controller.table_dump_entry(table_name,entry);
    def show_action(self):
        return self.controller.show_actions();
    def show_table_action(self,table_name):
        return self.controller.table_show_actions(table_name);
    def show_action_data(self,entry):
        return self.controller.dump_action_entry(entry);
    def table_dump_e(self,table_name,entry_handle):
        return self.controller.table_dump_entry(table_name,entry_handle);
    def mirroring_add_ids(self):
        self.controller.mirroring_add(100, 1)
    def check_and_add_table_entry(self, table_name, action_name, match_keys, action_params=[]):
        existing_entries = self.table_dump(table_name)
        match_key_str = str(match_keys)
        for entry in existing_entries:
            if match_key_str in str(entry):
                return
        self.table_add(table_name, action_name, match_keys, action_params)
    def write_register(self, register_name, index, value):
        self.controller.register_write(register_name, index, value)
    def _set_queue_rate(self, rate, port, priority):
        self.controller.set_queue_rate(rate, port, priority)

def find_smallest(data):
    indexed_data = list(enumerate(data))

    non_zero_data = [(index, value) for index, value in enumerate(data) if value != 0]
    sorted_indexed_data = sorted(non_zero_data, key=lambda x: x[1])
    first_smallest_index = sorted_indexed_data[0][0]+1
    second_smallest_index = sorted_indexed_data[1][0]+1
    #third_smallest_index = sorted_indexed_data[2][0]+1
    #fourth_smallest_index = sorted_indexed_data[3][0]+1
    return first_smallest_index, second_smallest_index


def write_array_to_file(filename, array):
    with open(filename, "w") as file:
        file.write(", ".join(map(str, array)))


def non_zero_length(array):
    non_zero_elements = [element for element in array if element != 0]
    return len(non_zero_elements)
def main():


       switch_name = 's1'
       port = 9090


       controller = Controller(switch_name)
       last_finish_time=  [0] *7
       process_array = []
       throughput = 0
       process_array=[]
       latency_array = []
       process_array_1 = []
       process_array_2 = []
       process_array_3 = []
       process_array_4 = []

       while not os.path.exists("traffic_signal.txt"):
        time.sleep(0.1)

       while not os.path.exists("stop_signal.txt"):
         deadline = controller.register_read("deadline",None)
         while non_zero_length(controller.register_read("deadline", None)) == 0:
             time.sleep(0.1)
             deadline = controller.register_read("deadline",None)
         value = controller.register_read("register_timestamp",None)
         weight = controller.register_read("weight",None)
         packet1 = controller.register_read("packet_length", None)

         slack = [0] * non_zero_length(deadline)

         for i in range(non_zero_length(deadline)):
            if deadline[i] == 0:
                   break
            slack[i] = deadline[i] - (0.1+ 11760 / 80000000)

         index1,index2 = find_smallest(slack)



         controller.table_add("set_priority_h","set_priority",[str(int(index1))])
         controller.table_add("set_priority_h","set_priority_8",[str(int(index2))])

         #controller.table_add("set_priority_h","set_priority_5",[str(int(index5))])
         #controller.table_add("set_priority_h","set_priority_6",[str(int(index6))])
         #controller.table_add("set_priority_h","set_priority_7",[str(int(index7))])
         value2 = controller.register_read("finish_time",None)
         for i in range(non_zero_length(deadline)):
            if deadline[i] == 0:
                   break
            process = value2[i] - value[i]
            latency = value[i] - last_finish_time[i]

            if process >0 and process not in process_array :
               process_array.append(process)
            if latency >0 and latency not in latency_array and latency>0:
               latency_array.append(latency)
            if deadline[i] + value[i] <=value2[i]:
               throughput +=1
         last_finish_time = value2.copy()

       print(f"latency: ",sum(latency_array)/len(latency_array))
       print(f"Throughput: ",throughput)
       #write_array_to_file("p1.txt", process_array_1)
       #write_array_to_file("p2.txt", process_array_2)
       #write_array_to_file("p3.txt", process_array_3)
       #write_array_to_file("p4.txt", process_array_4)
       write_array_to_file("pa.txt", process_array)
       if os.path.exists("stop_signal.txt"):
           os.remove("stop_signal.txt")
       if os.path.exists("traffic_signal.txt"):
           os.remove("traffic_signal.txt")



if __name__ == '__main__':
    main();
