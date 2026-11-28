cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(qrupdate REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE qrupdate::qrupdate)

if(QRUPDATE_STATIC)
    # The static library needs the Fortran runtime: link with the Fortran compiler, which provides it.
    # That compiler comes from the configuration (tools.build:compiler_executables), as for the library.
    enable_language(Fortran)
    set_target_properties(${PROJECT_NAME} PROPERTIES LINKER_LANGUAGE Fortran)
endif()
