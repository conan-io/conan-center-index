cmake_minimum_required (VERSION 3.15)
project (dbus_cxx_package_test CXX)

find_package (dbus-cxx REQUIRED CONFIG)

add_executable (test test.cpp)
target_link_libraries (test dbus-cxx::dbus-cxx)

