cmake_minimum_required(VERSION 3.1)

function(append string)
  file(APPEND "${output}" "${string}")
endfunction()

file(READ "${input}" content)

# BEGIN
set(havesection NO)
set(section "")
set(seclist "")
set(FNR 1)
get_filename_component(FILENAME "${input}" NAME)

file(WRITE "${output}" "\
/*
** This file generated automatically from ${FILENAME}
*/

#include \"defs.h\"
")

# body

string(REGEX REPLACE "\n$" "" content "${content}")
string(REPLACE "\\\n" "\\ \n" content "${content}")
string(REPLACE ";" "\;" content "${content}")
string(REPLACE "\n" ";" content "${content}")

foreach(line IN LISTS content)
  math(EXPR FNR "${FNR} + 1")
  string(REGEX REPLACE "\\\\ $" "\\\\" line "${line}")
  if(line MATCHES "^%%")
    if(havesection)
      append("    0\n};\n\n")
    endif()
    if(line MATCHES "^%% [^ ]+")
      string(SUBSTRING "${line}" 3 -1 section)
      set(havesection YES)
      list(APPEND seclist "${section}")
      append("static char *${section}[] =\n{\n")
      append("    \"#line ${FNR} \\\"${FILENAME}\\\"\",\n")
    else()
      set(havesection NO)
    endif()
    continue()
  endif()
  if(havesection)
    string(REPLACE "\\" "\\\\" line "${line}")
    string(REPLACE "\t" "\\t" line "${line}")
    string(REPLACE "\"" "\\\"" line "${line}")
    append("    \"${line}\",\n")
  else()
    append("${line}\n")
  endif()
endforeach()

# END

if(havesection)
  append("    0\n};\n\n")
endif()

if(NOT seclist STREQUAL "")
  append("struct section section_list[] = {\n")
  foreach(sec IN LISTS seclist)
    append("\t{ \"${sec}\", &${sec}[0] },\n")
  endforeach()
  append("\t{ 0, 0 } };\n")
endif()
