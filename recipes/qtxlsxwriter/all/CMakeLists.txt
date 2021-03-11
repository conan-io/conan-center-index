cmake_minimum_required(VERSION 3.1)

project(qtxlsxwriter)

add_subdirectory(src)

install(FILES LICENSE DESTINATION licenses)

set_property(GLOBAL PROPERTY AUTOGEN_SOURCE_GROUP "Generated Files")
