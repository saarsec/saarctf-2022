obj-m += r00t.o
r00t-objs := r00t-module.o

all:
	@make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
	#@ls -lh r00t.ko

containerbuild:
	@make -C /lib/modules/*-amd64/build M=$(PWD) modules

clean:
	@make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

test: all
	sudo dmesg -C
	@echo "Installing..."
	sudo insmod r00t.ko
	@echo "Installed."
	@sleep 1
	@ping 127.0.0.1 -c 1
	@python3 -u connecter.py
	@echo "Invoking client ..."
	@../cmake-build-debug-vm/r00t-client/r00t-client || echo "FAILED"
	@echo "Removing ..."
	sudo rmmod r00t.ko
	@echo "Removed."
	dmesg

install: all
	@sudo rmmod r00t.ko || echo "(no uninstall necessary)"
	sudo insmod r00t.ko

uninstall: all
	sudo rmmod r00t.ko
