#! /bin/sh
gitrev="`git show -q --oneline |cut -d ' ' -f1`"
exec docker build \
	--build-arg GITREV=${gitrev} \
	-t ret1:v0002 -t ret1:latest -t ret1:${gitrev} .
