cmake_minimum_required(VERSION 3.4)
project(libdisasm C)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(libdisasm_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

set(libdisasm_SRCS
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_implicit.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_implicit.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_insn.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_insn.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_invariant.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_invariant.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_modrm.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_modrm.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_opcode_tables.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_opcode_tables.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_operand.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_operand.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_reg.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_reg.h
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_settings.c
    ${libdisasm_SOURCE_DIR}/libdisasm/ia32_settings.h
    ${libdisasm_SOURCE_DIR}/libdisasm/libdis.h
    ${libdisasm_SOURCE_DIR}/libdisasm/qword.h
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_disasm.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_format.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_imm.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_imm.h
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_insn.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_misc.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_operand_list.c
    ${libdisasm_SOURCE_DIR}/libdisasm/x86_operand_list.h
)
add_library(disasm ${libdisasm_SRCS})
target_include_directories(disasm PRIVATE ${libdisasm_SOURCE_DIR}/libdisasm)

install(
  TARGETS disasm
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${libdisasm_SOURCE_DIR}/libdisasm/libdis.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
