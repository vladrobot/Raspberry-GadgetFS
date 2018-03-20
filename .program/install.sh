#!/bin/bash
file=/boot/config.txt

cp -R home/ /
cp -R etc/ /

st=(`cat $file |grep -e '^dtoverlay=dwc2'`)
if [ ${#st[@]} = 0 ]
then
    echo 'dtoverlay=dwc2' >> $file
fi

mkdir /home/pi/mnt
chown -R pi:pi /home/pi/mnt/ /home/pi/usbfs/ /home/pi/Desktop/
systemctl enable gadgetfs.service
#rm -r .program/

echo 'Install....OK'
echo 'Reboot system'
