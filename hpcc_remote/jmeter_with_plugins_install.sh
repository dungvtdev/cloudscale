#!/bin/bash

# ref 
# https://jmetervn.com/2016/12/14/how-to-install-plugins-in-jmeter-3-x-via-command-line/

JMETER=jmeter3.2
JMETER_HOME=$pwd/jmeter3.2
CURRENT_HOME=$pwd
# install jre
apt update

echo "******************************** Install default jre **********************************"
apt install default-jre

# download apache-jmeter
echo "******************************** Download apache jmeter ********************************"
wget http://mirrors.viethosting.com/apache//jmeter/binaries/apache-jmeter-3.2.tgz
tar -zxvf apache-jmeter-3.2.tgz 
mv apache-jmeter-3.2 $JMETER
cd $JMETER/

# download plugins jar
echo "******************************** Download plugins manager *******************************"
wget https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/0.13/jmeter-plugins-manager-0.13.jar
mv jmeter-plugins-manager-0.13.jar ./lib/ext/plugins-manager.jar

CMDRUNNER=cmdrunner-2.0.jar
if ! [ -f "$CMDRUNNER" ];
then
    wget https://repo1.maven.org/maven2/kg/apc/cmdrunner/2.0/cmdrunner-2.0.jar
    mv cmdrunner-2.0.jar ./lib/cmdrunner-2.0.jar
fi

PLUGINCMD=PluginsManagerCMD.sh
if ! [ -f "$PLUGINCMD" ];
then
    java -cp ./lib/ext/plugins-manager.jar org.jmeterplugins.repository.PluginManagerCMDInstaller
fi

# install plugins
echo "******************************** Install jmeter plugins ***********************************"
echo "********************** Install Ultimate Thread Group plugins ******************************"
./bin/PluginsManagerCMD.sh install jpgc-casutg

# back to current home
cd $CURRENT_HOME
