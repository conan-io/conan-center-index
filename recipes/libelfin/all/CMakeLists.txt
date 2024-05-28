cmake_minimum_required(VERSION 3.12)
project(libelfin CXX)

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PythonInterp 3 REQUIRED)

set(src ${CMAKE_CURRENT_LIST_DIR})

file(GLOB_RECURSE elf_sources ${src}/elf/*.cc)
set(elf_headers
    ${src}/elf/common.hh
    ${src}/elf/data.hh
    ${src}/elf/elf++.hh)
file(GLOB_RECURSE dwarf_sources ${src}/dwarf/*.cc)
set(dwarf_headers
    ${src}/dwarf/data.hh
    ${src}/dwarf/dwarf++.hh
    ${src}/dwarf/small_vector.hh)

add_custom_command(
    OUTPUT ${src}/elf/to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '// Automatically generated' > to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '// DO NOT EDIT' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '\#include \"data.hh\"' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '\#include \"to_hex.hh\"' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo 'ELFPP_BEGIN_NAMESPACE' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${PYTHON_EXECUTABLE} enum-print.py -u --hex --no-type --mask shf --mask pf -x loos -x hios -x loproc -x hiproc < data.hh >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo 'ELFPP_END_NAMESPACE' >> to_string.cc
    DEPENDS ${src}/elf/enum-print.py ${src}/elf/data.hh
    WORKING_DIRECTORY ${src}/elf)

add_custom_command(
    OUTPUT ${src}/dwarf/to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '// Automatically generated' > to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '// DO NOT EDIT' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo '\#include \"internal.hh\"' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo 'DWARFPP_BEGIN_NAMESPACE' >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo >> to_string.cc
    COMMAND ${PYTHON_EXECUTABLE} ../elf/enum-print.py < dwarf++.hh >> to_string.cc
    COMMAND ${PYTHON_EXECUTABLE} ../elf/enum-print.py -s _ -u --hex -x hi_user -x lo_user < data.hh >> to_string.cc
    COMMAND ${CMAKE_COMMAND} -E echo 'DWARFPP_END_NAMESPACE' >> to_string.cc
    DEPENDS ${src}/elf/enum-print.py ${src}/dwarf/data.hh
    WORKING_DIRECTORY ${src}/dwarf)

add_library(elf++ ${elf_sources} ${src}/elf/to_string.cc)
set_target_properties(elf++ PROPERTIES
    PUBLIC_HEADER "${elf_headers}"
    VERSION ${libelfin_VERSION})

add_library(dwarf++ ${dwarf_sources} ${src}/dwarf/to_string.cc)
set_target_properties(dwarf++ PROPERTIES
    PUBLIC_HEADER "${dwarf_headers}"
    VERSION ${libelfin_VERSION})

include(GNUInstallDirs)
install(TARGETS elf++
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libelfin/elf)
install(TARGETS dwarf++
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libelfin/dwarf)

install(FILES ${src}/LICENSE DESTINATION licenses)
