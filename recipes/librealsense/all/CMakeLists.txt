cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(libusb REQUIRED)
set(USB_FOUND TRUE)
add_library(usb INTERFACE IMPORTED GLOBAL)
target_link_libraries(usb INTERFACE libusb::libusb)

add_subdirectory("source_subfolder")
