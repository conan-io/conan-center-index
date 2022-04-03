cmake_minimum_required(VERSION 3.10.2)
project(test_package VERSION 1.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(ignition-cmake2 REQUIRED)

include(IgnCMake)

#===============================================================================
# test the functionality of ign_configure_project
# ign_setup_package() is called by the ing-cmake utility ign_configure_project()
# in Line 22, and that's why the function call is commented below
#===============================================================================
#ign_setup_packages()

#===============================================================================
# test the functionality of ign_configure_project
# internally this ign-cmake utility calls ign_setup_packages()
#===============================================================================
ign_configure_project()

#===============================================================================
# test the functionality of ign_configure_build
# should be called after ing_setup_packages() is called
#===============================================================================
ign_configure_build()


#============================================================================
# test the functionality of ign_create_docs
#============================================================================
configure_file(${PROJECT_SOURCE_DIR}/api.md.in ${PROJECT_BINARY_DIR}/api.md)
configure_file(${PROJECT_SOURCE_DIR}/tutorials.md.in ${PROJECT_BINARY_DIR}/tutorials.md)

ign_create_docs(
  API_MAINPAGE_MD "${PROJECT_BINARY_DIR}/api.md"
  TUTORIALS_MAINPAGE_MD "${PROJECT_BINARY_DIR}/tutorials.md"
)
