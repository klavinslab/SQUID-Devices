#!bin/sh
cp labprinter /etc/init.d/
chmod a+x /etc/init.d/labprinter
ln -s /etc/init.d/labprinter /etc/rc2.d/S30labprinter
ln -s /etc/init.d/labprinter /etc/rc6.d/K30labprinter
