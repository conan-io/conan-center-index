CFLAGS          += $(CONAN_CFLAGS)
CXXFLAGS        += $(CONAN_CXXFLAGS)
CPPFLAGS        += $(addprefix -I, $(CONAN_INCLUDE_DIRS))
CPPFLAGS        += $(addprefix -D, $(CONAN_DEFINES))
LDFLAGS         += $(addprefix -L, $(CONAN_LIB_DIRS))
LDLIBS          += $(addprefix -l, $(CONAN_LIBS))

ifneq ($(USE_SSE),)
vpath %.c sse
CFLAGS += -Isse
SOURCES = blake2b.c \
	  blake2bp.c \
	  blake2s.c \
	  blake2sp.c \
	  blake2xb.c \
	  blake2xs.c

else ifneq ($(USE_NEON),)
vpath %.c neon
CFLAGS += -Ineon
SOURCES = blake2b.c \
	  blake2bp.c \
	  blake2s-neon.c \
	  blake2xb.c \
	  blake2b-neon.c \
	  blake2s.c \
	  blake2sp.c \
	  blake2xs.c

else
vpath %.c ref
CFLAGS += -Iref
SOURCES = blake2bp-ref.c \
	  blake2b-ref.c \
	  blake2sp-ref.c \
	  blake2s-ref.c \
	  blake2xb-ref.c \
	  blake2xs-ref.c
endif

OBJECTS = $(patsubst %.c,%.o,$(SOURCES))

all: libblake2.a

libblake2.a: $(OBJECTS)
	$(AR) rc $@ $^
	$(AR) s $@

.PHONY: install
install: libblake2.a
	install -d $(DESTDIR)/include/blake2
	install -d $(DESTDIR)/lib
	install ref/blake2.h $(DESTDIR)/include/blake2/
	install libblake2.a $(DESTDIR)/lib/

.PHONY: clean
clean:
	rm -f $(OBJECTS) libblake2.a $(SOURCES:.c=.d)

%.d: %.c
	@set -e; rm -f $@; \
	 $(CC) -MM $(make) $< > $@.$$$$; \
	 sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	 rm -f $@.$$$$

include $(SOURCES:.c=.d)
