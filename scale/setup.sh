#!bin/sh
cp scale /etc/init.d/
chmod a+x /etc/init.d/scale
ln -s /etc/init.d/scale /etc/rc2.d/S31scale
ln -s /etc/init.d/scale /etc/rc6.d/K31scale
