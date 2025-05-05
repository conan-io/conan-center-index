cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)


find_package(OGRE ${OGRE_VERSION} COMPONENTS OgreMain REQUIRED)
add_executable(ogre_main ogre_main.cpp)
target_link_libraries(ogre_main OGRE::OgreMain)

set_target_properties(ogre_main PROPERTIES
CXX_STANDARD 11
CXX_STANDARD_REQUIRED ON
CXX_EXTENSIONS ON)
