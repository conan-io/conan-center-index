include(SOCI)

if( TARGET SOCI::soci_core )
    set_property(TARGET SOCI::soci_core PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CONAN_INCLUDE_DIRS_SOCI})
endif()

if( TARGET SOCI::soci_sqlite3 )
  set_property(TARGET SOCI::soci_sqlite3 PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CONAN_INCLUDE_DIRS_SQLITE3})
endif()

if( TARGET SOCI::soci_mysql )
  target_link_libraries(SOCI::soci_mysql INTERFACE CONAN_PKG::openssl CONAN_PKG::zlib)
  set_property(TARGET SOCI::soci_mysql PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CONAN_INCLUDE_DIRS_LIBMYSQLCLIENT})
endif()

if( TARGET SOCI::soci_odbc )
  target_link_libraries(SOCI::soci_odbc INTERFACE CONAN_PKG::libiconv)
  set_property(TARGET SOCI::soci_odbc PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CONAN_INCLUDE_DIRS_ODBC})
endif()

if( TARGET SOCI::soci_postgresql )
  set_property(TARGET SOCI::soci_postgresql PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CONAN_INCLUDE_DIRS_LIBPQ})
endif()