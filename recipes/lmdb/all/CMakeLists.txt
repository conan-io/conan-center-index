cmake_minimum_required(VERSION 3.4)
project(lmdb LANGUAGES C)

include(GNUInstallDirs)

# LMDB library:

add_library(lmdb
    ${LMDB_SRC_DIR}/lmdb.h
    ${LMDB_SRC_DIR}/mdb.c
    ${LMDB_SRC_DIR}/midl.c
    ${LMDB_SRC_DIR}/midl.h
)

set_target_properties(lmdb PROPERTIES
    PUBLIC_HEADER ${LMDB_SRC_DIR}/lmdb.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

find_package(Threads REQUIRED)
target_link_libraries(lmdb PUBLIC Threads::Threads)

install(TARGETS lmdb
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if (LMDB_ENABLE_ROBUST_MUTEX)
    target_compile_definitions(lmdb PUBLIC MDB_USE_ROBUST=1)
else (LMDB_ENABLE_ROBUST_MUTEX)
    target_compile_definitions(lmdb PUBLIC MDB_USE_ROBUST=0)
endif (LMDB_ENABLE_ROBUST_MUTEX)

# LMDB utilities:

if(NOT WIN32)
    foreach(TOOL mdb_stat mdb_copy mdb_dump mdb_load)
        add_executable(${TOOL} ${LMDB_SRC_DIR}/${TOOL}.c)
        target_link_libraries(${TOOL} lmdb)
        install(TARGETS ${TOOL} DESTINATION ${CMAKE_INSTALL_BINDIR})
    endforeach()
endif()
