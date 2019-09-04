PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

macro(use_cxx11)
  if(CMAKE_VERSION VERSION_LESS "3.1")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
      set (CMAKE_CXX_FLAGS "--std=gnu++11 ${CMAKE_CXX_FLAGS}")
    endif()
  else()
    set(CMAKE_CXX_STANDARD 11)
  endif()
endmacro(use_cxx11)

use_cxx11()


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(echo EchoServer.cpp)
TARGET_LINK_LIBRARIES(echo ${CONAN_LIBS})

ADD_EXECUTABLE(socket socket.cpp)
TARGET_LINK_LIBRARIES(socket ${CONAN_LIBS})

ADD_EXECUTABLE(md5 md5.cpp)
TARGET_LINK_LIBRARIES(md5 ${CONAN_LIBS})

ADD_EXECUTABLE(sample SampleApp.cpp)
TARGET_LINK_LIBRARIES(sample ${CONAN_LIBS})

ADD_EXECUTABLE(https Https.cpp)
TARGET_LINK_LIBRARIES(https ${CONAN_LIBS})

ADD_EXECUTABLE(sqlite SampleApp.cpp)
TARGET_LINK_LIBRARIES(sqlite ${CONAN_LIBS})

