cmake_minimum_required(VERSION 3.0)
project(SociTest)
enable_testing()

set(CMAKE_BUILD_TYPE "Debug")

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup(TARGETS)
conan_include_build_modules()

if (WITH_EMPTY)
    add_executable(empty_exe soci.cpp)
    target_compile_definitions(empty_exe PUBLIC BACKEND_EMPTY)
    target_link_libraries(empty_exe PUBLIC SOCI::soci_core SOCI::soci_empty)
    add_test(
        NAME TestSociEmpty
        COMMAND empty_exe
    )

endif()

if (WITH_SQLITE3)
    add_executable(sqlite3_exe soci.cpp)
    target_compile_definitions(sqlite3_exe PUBLIC BACKEND_SQLITE3)
    target_link_libraries(sqlite3_exe PUBLIC SOCI::soci_core SOCI::soci_sqlite3)
    add_test(
        NAME TestSociSqlite3
        COMMAND sqlite3_exe
    )
endif()

if (WITH_MYSQL)
    add_executable(mysql_exe mysql.cpp)
    target_compile_definitions(mysql_exe PUBLIC BACKEND_MYSQL)
    target_link_libraries(mysql_exe PUBLIC SOCI::soci_core SOCI::soci_mysql)
    add_test(
        NAME TestSociMysql
        COMMAND mysql_exe
    )
endif()

if (WITH_ODBC)
    add_executable(odbc_exe odbc.cpp)
    target_compile_definitions(odbc_exe PUBLIC BACKEND_ODBC)
    target_link_libraries(odbc_exe PUBLIC SOCI::soci_core SOCI::soci_odbc)
    add_test(
        NAME TestSociOdbc
        COMMAND odbc_exe
    )
endif()


if (WITH_POSTGRESQL)
    add_executable(postgresql_exe postgresql.cpp)
    target_compile_definitions(postgresql_exe PUBLIC BACKEND_POSTGRESQL)
    target_link_libraries(postgresql_exe PUBLIC SOCI::soci_core SOCI::soci_postgresql)
    add_test(
        NAME TestSociPostgreSQL
        COMMAND postgresql_exe
    )
endif()
