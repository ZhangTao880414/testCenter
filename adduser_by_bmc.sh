#/bin/bash

#循环获得当前bmc用户密码
function judgeActive()
{
    for myuser in ${USERLIST[@]}
    do
        for mypasswd in ${PASSWDLIST[@]}
        do
            ipmitool -H $IP_ADDR -U $myuser -P $mypasswd -I lanplus mc info &>/dev/null
            if [ $? -eq 0 ]
            then
                USER_NAME=$myuser
                PASSWD=$mypasswd
                echo "useful user and passwd for $IP_ADDR is : $USER_NAME   $PASSWD"
                return 0
            fi
        done
    done
    echo "usrename or passwd or ipaddr error,please check $IP_ADDR"
    echo "bmc user error for ip :$IP_ADDR " >>addfail.txt
    return 1
}

#添加bmc用户
function adduser()
{
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus user set name 5 qidian
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus user set password 5 qidian111
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus user priv 5 2 1
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus user priv 5 2 8
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus channel setaccess 1 5 callin=on ipmi=true link=on privilege=2
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus channel setaccess 8 5 callin=on ipmi=true link=on privilege=2
    ipmitool -H $IP_ADDR -U $USER_NAME -P $PASSWD -I lanplus user enable 5
}

#检查添加的新用户是否是活的
function checkUser()
{
    mySetPasswdlist=('qidian111' 'Qidian111' 'adminadmin$8' 'adminadmin$8.')
    for setPawsswd in ${mySetPasswdlist[@]}
    do
        ipmitool -I lanplus -H $IP_ADDR -U qidian -P $setPawsswd -L USER mc info &>/dev/null
        if [ $? -eq 0 ]
        then
            echo "$IP_ADDR qidian $setPawsswd is available for ip: $IP_ADDR"
            echo $IP_ADDR >>addok.txt
            return 0
        fi
    done
    echo "error: qidian not available for ip: $IP_ADDR "
    return 1
}

#检查ping可通
function checkPing()
{
    ping -c 1 $IP_ADDR &>/dev/null
    if [ $? -eq 0 ]
    then
        return 0
    fi
    echo "error: ping status is bad for ip:   $IP_ADDR" >>addfail.txt
    return 1
}

#通过ip批量检查ping状态
function  checkPingByIP()
{
    for LINE in `cat ip`;
    do 
    {
      IP_ADDR=`echo $LINE | awk -F, '{print $1}'| sed -e 's/[ ]*$//g'`
      checkPing
      if [ $? -eq 1 ]
      then
          echo "error: ping status is bad for ip:   $IP_ADDR"
          continue
      fi
    }
    done
}


#通过ip批量添加bmc用户
function addBmcByIP()
{
    for LINE in `cat ip`;
    do 
    {
      IP_ADDR=`echo $LINE | awk -F, '{print $1}'| sed -e 's/[ ]*$//g'`
      checkPing
      if [ $? -eq 1 ]
      then
          continue
      fi
      #检查超级用户密码能否登录bmc
      judgeActive
      if [ $? -eq 1 ]
      then
          continue
      fi
      #检查qidian用户是否存在，存在则退出，不存在则添加
      checkUser
      if [ $? -eq 1 ]
      then
          adduser    
      else
          continue
      fi
      checkUser
    }
    done
}

#通过ip批量检查bmc用户是否存在,存在则退出，不存在则添加
function checkUserExitByIP()
{
    for LINE in `cat ip`;
    do 
    {
      IP_ADDR=`echo $LINE | awk -F, '{print $1}'| sed -e 's/[ ]*$//g'`
      checkPing
      if [ $? -eq 1 ]
      then
          continue
      fi
      #检查qidian用户是否存在，存在则退出，不存在则添加
      checkUser
      if [ $? -eq 1 ]
      then
          echo "bmc USER NOT EXIT for ip :$IP_ADDR " >>addfail.txt  
      else
          continue
      fi
    }
    done

}

function showHelp()
{
    echo "1  : 更据ip批量添加qidian用户，qidian用户是否存在，存在则退出，不存在则添加"
    echo "2  : 更据ip 批量检查qidian用户是否存在,存在则退出，不存在则添加"
    echo "3  : 更据ip 批量检查ping状态"
    echo "h  : 显示帮助，参数信息"
}

USER_NAME='ADMIN'
PASSWD='Adminadmin$8'
USERLIST=('ADMIN' 'admin' 'administrator' 'root' 'USERID')
PASSWDLIST=('admin' 'Adminadmin$8' 'ADMIN' 'adminadmin$8' 'root123' 'PASSW0RD')

CHOOSE=$1
case $CHOOSE in
1)
  addBmcByIP
  ;;
2)
  checkUserExitByIP
  ;;
3)
  checkPingByIP
  ;;
"h")
  showHelp
  ;;
*)
  showHelp
  ;;
esac

