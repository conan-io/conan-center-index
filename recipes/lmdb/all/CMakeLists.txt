cmake_minimum_required(VERSION 2.8.12)
project (lmdb C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_DEBUG_POSTFIX "d")

set(SOURCES_PATH "source_subfolder/libraries/liblmdb")

add_library(lmdb-object OBJECT ${SOURCES_PATH}/mdb.c 
                               ${SOURCES_PATH}/midl.c)

add_library(lmdb-static STATIC $<TARGET_OBJECTS:lmdb-object>)
set_target_properties(lmdb-static PROPERTIES OUTPUT_NAME lmdb)

if(BUILD_SHARED_LIBS)
    add_library(lmdb-shared SHARED $<TARGET_OBJECTS:lmdb-object>)
    set_target_properties(lmdb-shared PROPERTIES OUTPUT_NAME lmdb)
endif()

if(NOT MSVC)
    add_executable(mdb_stat ${SOURCES_PATH}/mdb_stat.c)
    target_link_libraries(mdb_stat PRIVATE lmdb-static)

    add_executable(mdb_copy ${SOURCES_PATH}/mdb_copy.c)
    target_link_libraries(mdb_copy PRIVATE lmdb-static)

    add_executable(mdb_dump ${SOURCES_PATH}/mdb_dump.c)
    target_link_libraries(mdb_dump PRIVATE lmdb-static)

    add_executable(mdb_load ${SOURCES_PATH}/mdb_load.c)
    target_link_libraries(mdb_load PRIVATE lmdb-static)
endif()

if(BUILD_SHARED_LIBS)
    install(TARGETS lmdb-shared)
else()
    install(TARGETS lmdb-static)
endif()

if(NOT MSVC)
    install(TARGETS mdb_copy mdb_stat mdb_dump mdb_load)
endif()

install(FILES ${SOURCES_PATH}/lmdb.h DESTINATION include)
