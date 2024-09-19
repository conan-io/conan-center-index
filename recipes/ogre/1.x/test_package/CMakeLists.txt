cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(OGRE COMPONENTS OgreMain REQUIRED)

add_executable(ogre_main ogre_main.cpp)
target_link_libraries(ogre_main OgreMain)
target_compile_features(ogre_main PRIVATE cxx_std_11)
