cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_VERBOSE_MAKEFILE ON)

# Download and build .proto
file(READ ${CMAKE_BINARY_DIR}/conaninfo.txt CONAN_INFO)
string(REGEX MATCH "([0-9]+\\.[0-9]+\\.[0-9]+)" PACKAGE_VERSION ${CONAN_INFO})
if(NOT DEFINED PACKAGE_VERSION)
  message(FATAL_ERROR "Protobuf version not found")
endif()
string(TOLOWER ${CONAN_SETTINGS_OS} OS)
set(FILENAME "${CMAKE_CURRENT_SOURCE_DIR}/protoc.zip")
set(EXT "")
if(OS STREQUAL "windows")
  if(CONAN_SETTINGS_ARCH STREQUAL "x86_64")
    set(ARCH "64")
  elseif(CONAN_SETTINGS_ARCH STREQUAL "x86_32")
    set(ARCH "32")
  endif()  
  set(EXT ".exe")
  set(OS_ARCH "win${ARCH}")
elseif(OS STREQUAL "macos")
  set(OS_ARCH "osx-${CONAN_SETTINGS_ARCH}")
else()
  set(OS_ARCH "${OS}-${CONAN_SETTINGS_ARCH}")
endif(OS STREQ "Windows")

set(URL "https://github.com/protocolbuffers/protobuf/releases/download/v${PACKAGE_VERSION}/protoc-${PACKAGE_VERSION}-${OS_ARCH}.zip")
message("Download protoc binary from ${URL}")
file(DOWNLOAD ${URL} ${FILENAME} 
	      TIMEOUT 10
        STATUS res)
if(NOT res EQUAL 0)
  message(FATAL_ERROR "Download of protoc failed: ${res}")
endif()

execute_process(COMMAND "${CMAKE_COMMAND}" -E tar xzf "${FILENAME}"
                    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                    RESULT_VARIABLE res)
if(NOT res EQUAL 0)
  message(FATAL_ERROR "Unpack of protoc failed: ${res}")
endif()

execute_process(COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/bin/protoc${EXT}" "--proto_path=${CMAKE_CURRENT_SOURCE_DIR}" "--cpp_out=${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/addressbook.proto"
                    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                    RESULT_VARIABLE res)
if(NOT res EQUAL 0)
  message(FATAL_ERROR "Protoc compilation failed: ${res}")
endif()

file(REMOVE_RECURSE ${FILENAME} "${CMAKE_CURRENT_SOURCE_DIR}/bin" "${CMAKE_CURRENT_SOURCE_DIR}/include" "${CMAKE_CURRENT_SOURCE_DIR}/readme.txt")

# http://www.cmake.org/Wiki/CMake_FAQ#How_can_I_build_my_MSVC_application_with_a_static_runtime.3F
if(MSVC AND protobuf_MSVC_STATIC_RUNTIME)
  foreach(flag_var
      CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
      CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
    if(${flag_var} MATCHES "/MD")
      string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
    endif(${flag_var} MATCHES "/MD")
  endforeach()
endif()

add_executable(${PROJECT_NAME} test_package.cpp addressbook.pb.cc addressbook.pb.h)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
