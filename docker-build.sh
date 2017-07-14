#! /bin/sh
# TODO: image tag in rev-bump ext file
exec docker build -t ret1:v0002 -t ret1:latest .
