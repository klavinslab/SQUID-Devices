#!bin/sh
cp scale /etc/init.d/
chmod a+x /etc/init.d/scale
ln -s /etc/init.d/labprinter /etc/rc2.d/S31scale
