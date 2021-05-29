# From http://timelessname.com/elfbin/

hello: hello.asm
	nasm -f elf hello.asm
	gcc -m32 -s -o hello hello.o -nostartfiles -nostdlib -nodefaultlibs
