# Based on https://github.com/valgur/f2c/blob/20240312/makefile.u
cmake_minimum_required(VERSION 3.15)
project(f2c C)

# Configure sysdep.hd. Only sets NO_MKDTEMP and NO_MKSTEMP, if necessary.
if(MSVC)
    file(WRITE sysdep.hd "#define NO_MKDTEMP\n#define NO_MKSTEMP\n")
else()
    file(WRITE sysdep.hd "")
endif()

# Generate tokdefs.h
# grep -n . <tokens | sed "s/\([^:]*\):\(.*\)/#define \2 \1/" >tokdefs.h
file(STRINGS tokens TOKENS)
set(COUNTER 1)
set(TOKDEFS "")
foreach(TOKEN ${TOKENS})
  string(APPEND TOKDEFS "#define ${TOKEN} ${COUNTER}\n")
  math(EXPR COUNTER "${COUNTER} + 1")
endforeach()
file(WRITE tokdefs.h ${TOKDEFS})

add_executable(f2c
    main.c init.c gram.c lex.c proc.c equiv.c data.c format.c
    expr.c exec.c intr.c io.c misc.c error.c mem.c names.c
    output.c p1output.c pread.c put.c putpcc.c vax.c formatdata.c
    parse_args.c niceprintf.c cds.c sysdep.c version.c
)

install(TARGETS f2c DESTINATION bin)
