cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# LMDB library:

add_library(lmdb
    source_subfolder/lmdb.h
    source_subfolder/mdb.c
    source_subfolder/midl.c
    source_subfolder/midl.h
)

set_target_properties(lmdb PROPERTIES
    PUBLIC_HEADER source_subfolder/lmdb.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

include(FindThreads)
target_link_libraries(lmdb PUBLIC ${CMAKE_THREAD_LIBS_INIT})

install(TARGETS lmdb)

# LMDB utilities:

if(NOT WIN32)
    foreach(TOOL mdb_stat mdb_copy mdb_dump mdb_load)
        add_executable(${TOOL} source_subfolder/${TOOL}.c)
        target_link_libraries(${TOOL} lmdb)
        install(TARGETS ${TOOL})
    endforeach()
endif()
