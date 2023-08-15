#/bin/bash

user='qidian'
userPasswd='admin'
mySetPasswdlist=('qidian111' 'Qidian111' 'adminadmin$8' 'adminadmin$8.')
IP_ADDR=''

fileNameTime=$(date "+%Y%m%d%H%M%S")
time3=$(date "+%Y-%m-%d %H:%M:%S")
savefileneme=$(date +%Y%m%d)
filename=$savefileneme/$fileNameTime'-ipmiData.txt'

cpuTemp=' '
cpuFans=' '
sensorData=''
pingStatus='NO'
userAndPasswdStatus='NO'
originData=''

if [ ! -d "$savefileneme" ]
then
    mkdir $savefileneme
fi

if [ -f "$filename" ]
then
    rm -rf $filename
fi
touch $filename
echo $time3 > $filename

function setorgindata()
{
    cpuTemp=' '
    cpuFans=' '
    sensorData=''
    pingStatus='NO'
    userAndPasswdStatus='NO'
    originData=''
}

#检查ping可通
function checkPing()
{
    ping -c 1 $IP_ADDR &>/dev/null
    if [ $? -eq 0 ]
    then
        pingStatus='OK'
        return 0
    fi
    echo "error: ping status is bad for ip:   $IP_ADDR"
    pingStatus='NO'
    return 1
}

#检查qidian用户是否是活的
function checkUser()
{
    for setPawsswd in ${mySetPasswdlist[@]}
    do
        ipmitool -I lanplus -H $IP_ADDR -U qidian -P $setPawsswd -L USER mc info &>/dev/null
        if [ $? -eq 0 ]
        then
            userPasswd=$setPawsswd
            userAndPasswdStatus='OK'
            return 0
        fi
    done
    echo "error: qidian not available for ip: $IP_ADDR "
    userAndPasswdStatus='NO'
    return 1
}

function getCpuTemp()
{

    cpuTemp=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep  "cpu" |grep 'degrees c' |awk -F "|" '{gsub (" ","",$0);print $1 "|" $2+0 "|" $3}'`
    if [ -z "$cpuTemp" ]; then
        cpuTemp=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep "temp" |grep 'degrees c' |awk -F "|" '{if ($1="temp") print $1 "|" $2+0 "|" $3}'`
        if [ -z "$cpuTemp" ]; then
            cpuTemp=' '
            echo "cpuTemp is empty for $IP_ADDR"
        fi
    fi
}

function getCpuFans()
{
    cpuFans=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep 'fan' |grep -E 'rpm|percent' |awk -F "|" '{gsub (" ","",$0);print $1 "|" $2+0 "|" $3}'`
    if [ -z "$cpuFans" ]; then
        cpuFans=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep 'aio_pump' |grep -E 'rpm|percent' |awk -F "|" '{gsub (" ","",$0);print $1 "|" $2+0 "|" $3}'`
        if [ -z "$cpuFans" ]; then
            cpuFans=' '
            echo "cpuFans is empty for $IP_ADDR"
        fi
        
    fi
}
function getoriginData()
{
    originData=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep -E "cpu|temp|degrees|fan|rpm|percent" |grep -v "na"`
    if [ -z "$originData" ]; then
        originData=`ipmitool -I lanplus -H $IP_ADDR -U qidian -P $userPasswd -L USER sensor list |tr  [:upper:]  [:lower:]|grep -E "cpu|temp|degrees|fan|rpm|percent"`
        if [ -z "$originData" ]; then
            originData=' '
            echo "originData is empty for $IP_ADDR"
        fi
    fi

}

#设置数据为空
function saveDataEmety()
{
    cpuTemp=' '
    cpuFans=' '
    echo "---" >>$filename
    echo "ip:$IP_ADDR" >>$filename
    echo "cputemp:" >>$filename
    echo "$cpuTemp" >>$filename
    echo "fans:" >>$filename
    echo "$cpuFans" >>$filename
    echo "--" >> $filename
    echo "pingStatus: $pingStatus" >>$filename
    echo "userAndPasswdStatus: $userAndPasswdStatus" >>$filename
    echo "$originData">> $filename
    echo "--" >> $filename
    echo "---" >>$filename
}

#通过ip批量获取cpu 温度 和风扇状态
function  getCpuAndFanByIP()
{
    for LINE in `cat ip`;
    do 
    {
        IP_ADDR=`echo $LINE | awk -F, '{print $1}'| sed -e 's/[ ]*$//g'`
        setorgindata
        checkPing
        if [ $? -eq 1 ]
        then
          pingStatus='NO'
          saveDataEmety
          continue
        fi
        checkUser
        if [ $? -eq 1 ]
        then
          userAndPasswdStatus='NO'
          saveDataEmety
          continue
        fi
        echo "get data for :$IP_ADDR"
        getCpuTemp
        getCpuFans
        getoriginData
        echo "---" >>$filename
        echo "ip:$IP_ADDR" >>$filename
        echo "cputemp:" >>$filename
        echo "$cpuTemp" >>$filename
        echo "fans:" >>$filename
        echo "$cpuFans" >>$filename
        echo "--" >> $filename
        echo "pingStatus: $pingStatus" >>$filename
        echo "userAndPasswdStatus: $userAndPasswdStatus" >>$filename
        echo "$originData">> $filename
        echo "--" >> $filename
        echo "---" >>$filename
    }
    done
}
getCpuAndFanByIP