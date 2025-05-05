cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)

if(MSVC)
  # Should be added because of
  # https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-initonceexecuteonce
  add_definitions(-D_WIN32_WINNT=0x0600)
endif()
