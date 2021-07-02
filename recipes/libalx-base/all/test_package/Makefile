CC := cc

CFLAGS := $(shell pkg-config --cflags libalx-base)
LIBS   := $(shell pkg-config --libs   libalx-base)

.PHONY: all
.PHONY: build

all:   build
build: test_package

test_pkg: main.c
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)
