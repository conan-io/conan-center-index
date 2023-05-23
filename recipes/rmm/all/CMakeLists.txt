cmake_minimum_required(VERSION 3.15)
project(RMM CXX)

if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/RMM_RAPIDS.cmake)
  file(DOWNLOAD https://raw.githubusercontent.com/rapidsai/rapids-cmake/branch-23.04/cmake/write_version_file.cmake
       ${CMAKE_CURRENT_BINARY_DIR}/write_version_file.cmake)
endif()
include(${CMAKE_CURRENT_BINARY_DIR}/write_version_file.cmake)

rapids_cmake_write_version_file(include/rmm/version_config.hpp)
install(DIRECTORY include/rmm/ DESTINATION include/rmm)
install(FILES ${RMM_BINARY_DIR}/include/rmm/version_config.hpp DESTINATION include/rmm)
