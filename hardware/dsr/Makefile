
#
# : DSR for TIPI, multi purpose Raspberry PI enabled device. 
# 
# Use xas99 
#

XAS99?=$(shell which xas99.py)

all: tipi.bin

sources = rom.a99 header.a99 vdp-io.a99 tipi-io.a99 powerup.a99 devices.a99 loadea5.a99 opt5.a99 basic.a99 level2.a99 dsrlist.a99

clean:
	-rm *.list >/dev/null 2>&1
	-rm tipi*.bin timestamp.gen >/dev/null 2>&1

tipi.bin: $(sources) timestamp.gen
	python3 $(XAS99) -R -b -L tipi.list -o $@ rom.a99
	dd if=/dev/null of=$@ bs=1 count=0 seek=32768

timestamp.gen:
	TIMESTAMP=`date --iso-8601="seconds"`; ( echo "	TEXT	\"$$TIMESTAMP\""; echo "	BYTE	0"; echo "	EVEN" ) >timestamp.gen

.PHONY: burn flash

burn: tipi.bin
	minipro -p "AM27C256@DIP28" -w tipi.bin -y

flash: tipi.bin
	minipro -p "AT29C256@DIP28" -w tipi.bin -y

