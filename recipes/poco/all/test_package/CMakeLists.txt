cmake_minimum_required(VERSION 3.0)
project(MyHello)

macro(use_cxx11)
  if(CMAKE_VERSION VERSION_LESS "3.1")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
      set (CMAKE_CXX_FLAGS "--std=gnu++11 ${CMAKE_CXX_FLAGS}")
    endif()
  else()
    set(CMAKE_CXX_STANDARD 11)
  endif()
endmacro()

use_cxx11()


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(echo EchoServer.cpp)
target_link_libraries(echo ${CONAN_LIBS})

add_executable(socket socket.cpp)
target_link_libraries(socket ${CONAN_LIBS})

add_executable(md5 md5.cpp)
target_link_libraries(md5 ${CONAN_LIBS})

add_executable(sample SampleApp.cpp)
target_link_libraries(sample ${CONAN_LIBS})

add_executable(https Https.cpp)
target_link_libraries(https ${CONAN_LIBS})

add_executable(sqlite SampleApp.cpp)
target_link_libraries(sqlite ${CONAN_LIBS})
