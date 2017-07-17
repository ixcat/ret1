#! /bin/sh

dbready=0;
while [ "$dbready" -eq "0" ]; do
	sleep 5;
	echo '# waiting for db init to complete';
	mysqladmin -u ${DJ_USER} -p${DJ_PASS} -h ${DJ_HOST} status
	if [ "$?" -eq "0" ]; then
		dbready=1;
	fi
done

echo '# running test';
/usr/local/bin/ret1_test.py /data/Data;

