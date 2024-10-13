/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

register <bit<48>>(20) register_timestamp;
register <bit<48>>(20) finish_time;
register <bit<64>>(20) deadline;
register <bit<32>>(20) weight;
register <bit<16>>(20) packet_length;
register <bit<3>>(20) priority;


header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    tos;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header udp_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length;
    bit<16> checksum;
    bit<64> deadline;
    bit<32> weight;
    bit<32> flow_id;

}

struct metadata {
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    udp_t        udp_deadline;

}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){

            TYPE_IPV4: ipv4;
            default: accept;
        }

    }

    state ipv4 {

        packet.extract(hdr.ipv4);

        transition select(hdr.ipv4.protocol) {
           0x11: udp;
           default: accept;
     }
  }
    state udp {
       packet.extract(hdr.udp_deadline);
       transition accept;
}

}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {

        // Set the src mac address as the previous dst, this is not correct right?
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        // Set the destination mac address that we got from the match in the table
        hdr.ethernet.dstAddr = dstAddr;

        // Set the output port that we also get from the table
        standard_metadata.egress_spec = port;

        // Decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl -1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    action set_priority(){

       standard_metadata.priority = (bit<3>)7;

    }
    action set_priority_2(){
       standard_metadata.priority = (bit<3>)6;
    }
    action set_priority_3(){
       standard_metadata.priority = (bit<3>)5;
    }
    action set_priority_4(){
       standard_metadata.priority = (bit<3>)4;
    }
    action set_priority_5(){
       standard_metadata.priority = (bit<3>)3;
    }
    action set_priority_6(){
       standard_metadata.priority = (bit<3>)2;
    }
    action set_priority_7(){
       standard_metadata.priority = (bit<3>)1;
    }
    action set_priority_8(){
       standard_metadata.priority = (bit<3>)0;
    }


    table set_priority_h{
        key = {
            hdr.udp_deadline.weight:exact;
        }
        actions = {
            set_priority;
            set_priority_2;
            set_priority_3;
            set_priority_4;
            set_priority_5;
            set_priority_6;
            set_priority_7;
            set_priority_8;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        // Only if IPV4 the rule is applied. Therefore other packets will not be forwarded.
        bit<3> priority_value;
        if (hdr.ipv4.isValid()){

            register_timestamp.write(hdr.udp_deadline.weight-1,standard_metadata.ingress_global_timestamp);
            deadline.write(hdr.udp_deadline.weight-1,hdr.udp_deadline.deadline);
            weight.write(hdr.udp_deadline.weight-1,hdr.udp_deadline.weight);
            packet_length.write(hdr.udp_deadline.weight-1,hdr.ipv4.totalLen);
            ipv4_lpm.apply();
            set_priority_h.apply();

        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

   apply {
        hdr.ipv4.tos = (bit<8>)standard_metadata.qid;

        finish_time.write(hdr.udp_deadline.weight-1,standard_metadata.egress_global_timestamp);



        }
    }


/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.tos,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
