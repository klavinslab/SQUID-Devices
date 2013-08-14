#!bin/sh
cp refrigerator /etc/init.d/
chmod a+x /etc/init.d/refrigerator
ln -s /etc/init.d/refrigerator /etc/rc2.d/S32refrigerator
ln -s /etc/init.d/refrigerator /etc/rc6.d/K32refrigerator
