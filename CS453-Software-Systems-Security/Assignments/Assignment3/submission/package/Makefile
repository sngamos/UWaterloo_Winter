# Targets
all: sploit1 sploit2 sploit3 sploit4

# sandbox1: compile normally (no static linking required)
sploit1: sploit1.c
	gcc -o sploit1 sploit1.c

# sandbox2: avoid C runtime startup, use static linking and -nostdlib
sploit2: sploit2.c
	gcc -static -nostdlib -o sploit2 sploit2.c

# sandbox3: compile as a static 64-bit binary with optimization
sploit3: sploit3.c
	gcc -m64 -static -O2 -Wno-pointer-to-int-cast -nostdlib -o sploit3 sploit3.c

# sandbox4: compile as an x32 binary with static linking and -nostdlib
sploit4: sploit4.c
	gcc -mx32 -static -nostdlib -O2 -o sploit4 sploit4.c

clean:
	rm -f sploit1 sploit2 sploit3 sploit4
