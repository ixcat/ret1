# TODO: test

all: extract_data build_image run_image

extract_data:
	unzip *.zip

build_image:
	./docker-build.sh

run_image:
	./stack.sh
