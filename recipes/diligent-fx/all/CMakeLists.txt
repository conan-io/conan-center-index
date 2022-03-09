cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(diligent-core)
find_package(diligent-tools)

if(WIN32)
  set(FILE2STRING_PATH "${CONAN_BIN_DIRS_DILIGENT-CORE}/File2String.exe")
else()
  set(FILE2STRING_PATH "${CONAN_BIN_DIRS_DILIGENT-CORE}/File2String")
endif()

include(BuildUtils.cmake)
add_subdirectory(source_subfolder)
