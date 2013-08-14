#!bin/sh
cp refrigerator /etc/init.d/
chmod a+x /etc/init.d/refrigerator
ln -s /etc/init.d/labprinter /etc/rc2.d/S32refrigerator
