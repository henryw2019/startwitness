#!/bin/bash
 
# /*
# *
# * Auto setup and run an witness of citshares
# * AUTHOR : ioex.henry
# * Date   : 2019-04-28
# *
# *
# */
 
usage()
{
    echo ""
    echo "startwitness.sh --> show this message"
    echo "startwitness.sh install --> install witness"
    echo "startwitness.sh start  --> start witness application"
    echo ""
} 

call_cli_wallet()
{
    cmd="$1"
    (echo "unlock 123456" ;sleep 3;echo "$cmd";sleep 3;echo "quit" )|./cli_wallet -s ws://127.0.0.1:11010 2>/dev/null
}

set_cli_wallet()
{
    cmd="$1"
    (echo "set_password 123456" ;sleep 3;echo "$cmd";sleep 3;echo "quit" )|./cli_wallet -s ws://127.0.0.1:11010 2>/dev/null
}

startwit()
{
    nohup ./witness_node --replay-blockchain >/dev/null 2>&1 &
}

install()
{
    read -p "Please enter your ACCOUNT:" ACCOUNT
    read -p "Please enter your PRIVATEKEY:" PRIVATEKEY
    
    #安装依赖
    sudo apt-get update
    sudo apt-get -y install autoconf cmake make automake libtool git libboost-all-dev libssl-dev g++ libcurl4-openssl-dev
    
    #下载cli_wallet  witness_node
    wget https://github.com/citshares/bitshares-core/releases/download/v1.0.0/witness_node
    wget https://github.com/citshares/bitshares-core/releases/download/v1.0.0/cli_wallet
    
    chmod +x witness_node cli_wallet
    
    ctsbalance=`call_cli_wallet "list_account_balances $ACCOUNT" |grep CTS|cut -d" " -f 1`
    
    if [ "$ctsbalance" == "" -o $ctsbalance -lt 1000 ];then
        echo "Your [$ACCOUNT] balance [$ctsbalance] lower than 1000 CTS,please recharge and continue."
        return -1
    fi
    
    set_cli_wallet "import_key \"$ACCOUNT\" $PRIVATEKEY true"
    
    call_cli_wallet "upgrade_account $ACCOUNT true"
    
    call_cli_wallet "create_witness my-account "http://auto.setup" true"
    
    witnessid = `call_cli_wallet "get_witness $ACCOUNT"|grep "\"id\": \""|grep -o "\"1.6.[0-9]*\""`
    
    signing_key = `call_cli_wallet "get_witness $ACCOUNT"|grep "\"signing_key\": \""|awk -F'"' '{print $4}'`
    
    signing_privatekey = `call_cli_wallet "dump_private_keys"|xargs|grep -o "$signing_key, [0-9a-zA-Z]*"|awk -F' ' '{print $2}'`
    
    #配置config.ini 文件
    sed -i 's/# p2p-endpoint =/p2p-endpoint = 0.0.0.0:11010/g' witness_node_data_dir/config.ini
    sed -i 's/# seed-node =/seed-node = 204.152.201.94:45529/g' witness_node_data_dir/config.ini
    sed -i 's/# witness-id =/witness-id = "$witnessid" /g' witness_node_data_dir/config.ini
    sed -i 's/CTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV/"$signing_key"/g' witness_node_data_dir/config.ini
    sed -i 's/5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3/"$signing_privatekey"/g' witness_node_data_dir/config.ini
    
    
    echo " Congratulations , Now you can run witness by : startwitness.sh start "
    echo " When the votes reaches a certain level, your witness will produce blocks."
    echo " HAVE FUN"
    
    
}

#------------------------start-------------------------------------------
set -e

mkdir -p citshares-witness
cd citshares-witness

if [ "$1" != "start" -a "$1" != "install" ];then
    usage
    exit
fi

if [ "$1" == "start" ];then
    startwit &
    exit
fi

if [ "$1" == "install" ];then
    install
    exit
fi
#------------------------ end -------------------------------------------