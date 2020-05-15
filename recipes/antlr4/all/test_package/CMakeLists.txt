cmake_minimum_required(VERSION 3.10)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${PROJECT_NAME} main.cpp
   generated/TLexer.cpp
   generated/TParser.cpp
   generated/TParserBaseListener.cpp
   generated/TParserBaseVisitor.cpp
   generated/TParserListener.cpp
   generated/TParserVisitor.cpp
   )

target_link_libraries(${PROJECT_NAME} PUBLIC ${CONAN_LIBS})
target_include_directories(${PROJECT_NAME} PUBLIC generated)

if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
   target_compile_options(${PROJECT_NAME} PUBLIC "-Wno-overloaded-virtual")
else ()
   target_compile_options(${PROJECT_NAME} PUBLIC "-MP /wd4251")
endif ()
