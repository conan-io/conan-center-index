cmake_minimum_required(VERSION 3.7)
project(cspice LANGUAGES C)

include(GNUInstallDirs)

option(CSPICE_BUILD_UTILITIES "Build cspice utilities" ON)

add_compile_options(
  $<$<OR:$<C_COMPILER_ID:GNU>,$<C_COMPILER_ID:AppleClang>>:-Wno-implicit-int>
  $<$<OR:$<C_COMPILER_ID:GNU>,$<C_COMPILER_ID:AppleClang>>:-Wno-format>
  $<$<OR:$<C_COMPILER_ID:GNU>,$<C_COMPILER_ID:AppleClang>>:-Wno-pointer-to-int-cast>
  $<$<C_COMPILER_ID:AppleClang>:-Wno-logical-op-parentheses>
  $<$<C_COMPILER_ID:AppleClang>:-Wno-shift-op-parentheses>
  $<$<C_COMPILER_ID:AppleClang>:-Wno-parentheses>
  $<$<C_COMPILER_ID:AppleClang>:-Wno-dangling-else>
  $<$<C_COMPILER_ID:AppleClang>:-Wno-unsequenced>
  $<$<C_COMPILER_ID:MSVC>:/wd4101>
  $<$<C_COMPILER_ID:MSVC>:/wd4244>
  $<$<C_COMPILER_ID:MSVC>:/wd4267>
  $<$<C_COMPILER_ID:MSVC>:/wd4311>
  $<$<C_COMPILER_ID:MSVC>:/wd4477>
  $<$<C_COMPILER_ID:MSVC>:/wd4554>
  $<$<C_COMPILER_ID:MSVC>:/wd4723>
  $<$<C_COMPILER_ID:MSVC>:/wd4996>
  # Behavior of implicitly defined functions changed in AppleClang 12
  # https://developer.apple.com/documentation/xcode-release-notes/xcode-12-release-notes
  $<$<AND:$<C_COMPILER_ID:AppleClang>,$<VERSION_GREATER_EQUAL:${CMAKE_C_COMPILER_VERSION},12>>:-Wno-error=implicit-function-declaration>
)

set(SRC_DIR ${CSPICE_SRC_DIR}/src)

file(GLOB CSPICE_SRC_FILES ${SRC_DIR}/cspice/*.c)
add_library(cspice ${CSPICE_SRC_FILES})

if(WIN32)
  target_compile_definitions(cspice PRIVATE "_COMPLEX_DEFINED;MSDOS;OMIT_BLANK_CC;NON_ANSI_STDIO;_CRT_SECURE_NO_WARNINGS")
  set_target_properties(cspice PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
elseif(UNIX)
  target_compile_definitions(cspice PRIVATE "NON_UNIX_STDIO")
  target_compile_options(cspice PRIVATE -ansi)
endif()

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  target_link_libraries(cspice PRIVATE m)
endif()

install(
  TARGETS cspice
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

file(GLOB INCLUDE_FILES ${CSPICE_SRC_DIR}/include/*.h)
install(FILES ${INCLUDE_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(CSPICE_BUILD_UTILITIES)
  # csupport is common to all utilities
  file(GLOB CSUPPORT_SRC_FILES "${SRC_DIR}/csupport/*.c")
  add_library(csupport STATIC ${CSUPPORT_SRC_FILES})

  # Walk into all utilities subfolders and build them (except cook_c which only contains examples)
  file(GLOB CSPICE_UTILITIES_SUBDIRS RELATIVE ${SRC_DIR} "${SRC_DIR}/*_c")
  list(REMOVE_ITEM CSPICE_UTILITIES_SUBDIRS "cook_c")
  foreach(CSPICE_SUBDIR ${CSPICE_UTILITIES_SUBDIRS})
    set(UTILITY_SRC_DIR "${SRC_DIR}/${CSPICE_SUBDIR}")

    # Each .pgm file is the entry point of an executable
    file(GLOB PGM_FILES "${UTILITY_SRC_DIR}/*.pgm")

    # Source files common to all executables in this subfolder
    # Ignore these files: main.c, <pgmfilename>.c, <pgmfilename>_main.c
    # (might have been pre-generated, specially in Windows source code)
    file(GLOB CSPICE_UTILITY_SRC_FILES ${UTILITY_SRC_DIR}/*.c)
    get_filename_component(MAIN_SRC_FILE "${UTILITY_SRC_DIR}/main.c" ABSOLUTE)
    list(REMOVE_ITEM CSPICE_UTILITY_SRC_FILES "${MAIN_SRC_FILE}")
    foreach(PGM_FILE ${PGM_FILES})
      get_filename_component(CSPICE_UTILITY ${PGM_FILE} NAME_WE)
      get_filename_component(PGM_MAIN_SRC_FILE "${UTILITY_SRC_DIR}/${CSPICE_UTILITY}_main.c" ABSOLUTE)
      get_filename_component(GENERIC_MAIN_SRC_FILE "${UTILITY_SRC_DIR}/${CSPICE_UTILITY}.c" ABSOLUTE)
      list(REMOVE_ITEM CSPICE_UTILITY_SRC_FILES "${PGM_MAIN_SRC_FILE}" "${GENERIC_MAIN_SRC_FILE}")
    endforeach()
    if(CSPICE_UTILITY_SRC_FILES)
      add_library(${CSPICE_SUBDIR}_commonlib OBJECT ${CSPICE_UTILITY_SRC_FILES})
    endif()

    # Build one executable per pgm file
    foreach(PGM_FILE ${PGM_FILES})
      get_filename_component(CSPICE_UTILITY ${PGM_FILE} NAME_WE)

      # Generate <pgm_filename>_main.c file from .pgm file
      set(PGM_MAIN_SRC_FILE "${CMAKE_CURRENT_BINARY_DIR}/cspice_generated/${CSPICE_SUBDIR}/${CSPICE_UTILITY}_main.c")
      add_custom_target(${CSPICE_UTILITY}_PGM DEPENDS ${PGM_FILE} ${PGM_MAIN_SRC_FILE})
      add_custom_command(
        OUTPUT ${PGM_MAIN_SRC_FILE}
        DEPENDS ${PGM_FILE}
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${PGM_FILE} ${PGM_MAIN_SRC_FILE}
      )

      # Generate <pgm_filename>.c from main.x file if it exists
      set(INPUT_MAIN_FILE "${UTILITY_SRC_DIR}/main.x")
      set(GENERIC_MAIN_SRC_FILE "")
      if(EXISTS ${INPUT_MAIN_FILE})
        set(GENERIC_MAIN_SRC_FILE "${CMAKE_CURRENT_BINARY_DIR}/cspice_generated/${CSPICE_SUBDIR}/${CSPICE_UTILITY}.c")
        add_custom_target(${CSPICE_UTILITY}_MAIN DEPENDS ${INPUT_MAIN_FILE} ${GENERIC_MAIN_SRC_FILE})
        add_custom_command(
          OUTPUT ${GENERIC_MAIN_SRC_FILE}
          DEPENDS ${INPUT_MAIN_FILE}
          COMMAND ${CMAKE_COMMAND} -E copy_if_different ${INPUT_MAIN_FILE} ${GENERIC_MAIN_SRC_FILE}
        )
      endif()

      add_executable(${CSPICE_UTILITY} ${PGM_MAIN_SRC_FILE} ${GENERIC_MAIN_SRC_FILE})
      add_dependencies(${CSPICE_UTILITY} ${CSPICE_UTILITY}_PGM)
      if(TARGET ${CSPICE_UTILITY}_MAIN)
        add_dependencies(${CSPICE_UTILITY} ${CSPICE_UTILITY}_MAIN)
      endif()
      target_include_directories(${CSPICE_UTILITY} PRIVATE ${UTILITY_SRC_DIR})
      target_link_libraries(${CSPICE_UTILITY} PRIVATE csupport cspice)
      if(TARGET ${CSPICE_SUBDIR}_commonlib)
        target_link_libraries(${CSPICE_UTILITY} PRIVATE ${CSPICE_SUBDIR}_commonlib)
      endif()
      if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        target_link_libraries(${CSPICE_UTILITY} PRIVATE m)
      endif()
      install(TARGETS ${CSPICE_UTILITY} DESTINATION ${CMAKE_INSTALL_BINDIR})
    endforeach()
  endforeach()
endif()
