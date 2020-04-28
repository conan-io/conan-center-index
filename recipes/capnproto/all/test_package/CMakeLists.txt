cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

function(target_capn_schemas TARGET)
  if(NOT ARGN)
    message(SEND_ERROR "target_capn_sources() called without any source files.")
  endif()

  if(NOT CAPNP_EXE)
    find_program(CAPNP_EXE NAMES capnp)
    if(NOT CAPNP_EXE)
      message(FATAL_ERROR "capnp not found!")
    endif()
  endif()

  if(NOT CAPNP_CXX_EXE)
    find_program(CAPNP_CXX_EXE NAMES capnpc-c++)
    if(NOT CAPNP_CXX_EXE)
      message(FATAL_ERROR "capnpc-c++ not found!")
    endif()
  endif()

  foreach(SCHEMA_FILE ${ARGN})
    get_filename_component(FILE_NAME ${SCHEMA_FILE} NAME)
    set(CAPNPC_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/${FILE_NAME}.compiled")
    set(SOURCE_FILE "${CAPNPC_OUTPUT_DIR}/${FILE_NAME}.c++")

    set(CAPN_GENERATE_TARGET "capn_generate_${FILE_NAME}")
    if(NOT TARGET ${CAPN_GENERATE_TARGET})
      get_filename_component(FILE_ABS_PATH ${SCHEMA_FILE} ABSOLUTE)
      get_filename_component(FILE_DIR "${FILE_ABS_PATH}" PATH)
      add_custom_command(
        OUTPUT ${SOURCE_FILE}
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CAPNPC_OUTPUT_DIR}
        COMMAND ${CMAKE_COMMAND} -E env
                LD_LIBRARY_PATH=${CONAN_LIB_DIRS_CAPNPROTO}:$ENV{LD_LIBRARY_PATH}
                DYLD_LIBRARY_PATH=${CONAN_LIB_DIRS_CAPNPROTO}:$ENV{DYLD_LIBRARY_PATH}
                ${CAPNP_EXE}
        ARGS compile
             -I ${CONAN_INCLUDE_DIRS_CAPNPROTO} # mandatory if .capnp set a Namespace !
             --no-standard-import
             -o ${CAPNP_CXX_EXE}:${CAPNPC_OUTPUT_DIR}
             --src-prefix ${FILE_DIR}
             ${FILE_ABS_PATH}
        DEPENDS ${FILE_ABS_PATH}
        COMMENT "Compiling Cap'n Proto schema ${SCHEMA_FILE}"
      )
      add_custom_target(${CAPN_GENERATE_TARGET} DEPENDS ${SOURCE_FILE})
    endif()

    add_dependencies(${TARGET} ${CAPN_GENERATE_TARGET})
    target_sources(${TARGET} PRIVATE ${SOURCE_FILE})
    target_include_directories(${TARGET} PRIVATE ${CAPNPC_OUTPUT_DIR})
  endforeach()
endfunction()

add_executable(addressbook addressbook.c++)
target_capn_schemas(addressbook addressbook.capnp)
target_link_libraries(addressbook ${CONAN_LIBS})
set_property(TARGET addressbook PROPERTY CXX_STANDARD 14)

if(NOT CAPNP_LITE)
  add_executable(calculator-client calculator-client.c++)
  target_capn_schemas(calculator-client calculator.capnp)
  target_link_libraries(calculator-client ${CONAN_LIBS})
  set_property(TARGET calculator-client PROPERTY CXX_STANDARD 14)

  add_executable(calculator-server calculator-server.c++)
  target_capn_schemas(calculator-server calculator.capnp)
  target_link_libraries(calculator-server ${CONAN_LIBS})
  set_property(TARGET calculator-server PROPERTY CXX_STANDARD 14)
endif()
