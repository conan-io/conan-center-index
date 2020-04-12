cmake_minimum_required(VERSION 3.1.2)
project(soci)


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
add_subdirectory(source_subfolder)

cmake_policy(SET CMP0079 NEW)

if( CMAKE_SYSTEM_NAME STREQUAL "Windows" )

  target_link_libraries(soci_postgresql ${CONAN_SYSTEM_LIBS_LIBPQ})
  foreach(LIBPQ IN LISTS CONAN_PKG_LIBS_LIBPQ)
    find_library(
      PQ_LIBRARY
      name ${LIBPQ}
      PATHS ${CONAN_LIB_DIRS_LIBPQ}
    )
    target_link_libraries(soci_postgresql ${PQ_LIBRARY})
    unset(PQ_LIBRARY CACHE)
  endforeach()

  target_link_libraries(soci_mysql CONAN_PKG::zlib)

endif()