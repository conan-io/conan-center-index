# based on: https://github.com/microsoft/vcpkg/blob/master/ports/quickfast/CMakeLists.txt
# modified to fix warnings (BOOST_BIND_NO_PLACEHOLDERS)

# Copyright (c) Microsoft Corporation

# All rights reserved.

# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

cmake_minimum_required(VERSION 3.13)
project(quickfast CXX)

include(${PROJECT_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

option(BUILD_SHARED_LIBS "Build shared instead of static library" ON)

option(BOOST_BIND_NO_PLACEHOLDERS "BOOST_BIND_NO_PLACEHOLDERS" ON)

file(GLOB SOURCES
	${PROJECT_SOURCE_DIR}/src/Application/*.cpp
	${PROJECT_SOURCE_DIR}/src/Common/*.cpp
	${PROJECT_SOURCE_DIR}/src/Codecs/*.cpp
	${PROJECT_SOURCE_DIR}/src/Communication/*.cpp
	${PROJECT_SOURCE_DIR}/src/Messages/*.cpp
)

file(GLOB HEADERS RELATIVE ${PROJECT_SOURCE_DIR}
	${PROJECT_SOURCE_DIR}/src/Application/*.h
	${PROJECT_SOURCE_DIR}/src/Common/*.h
	${PROJECT_SOURCE_DIR}/src/Codecs/*.h
	${PROJECT_SOURCE_DIR}/src/Communication/*.h
	${PROJECT_SOURCE_DIR}/src/Messages/*.h
)

if(BUILD_SHARED_LIBS)
	add_library(quickfast SHARED ${HEADERS} ${SOURCES})
	target_compile_definitions(quickfast PRIVATE -DQUICKFAST_BUILD_DLL)
else()
	add_library(quickfast STATIC ${HEADERS} ${SOURCES})
	target_compile_definitions(quickfast PUBLIC -DQUICKFAST_HAS_DLL=0)
endif()

if(BOOST_BIND_NO_PLACEHOLDERS)
	target_compile_definitions(quickfast PRIVATE BOOST_BIND_NO_PLACEHOLDERS)
endif()

target_include_directories(quickfast PUBLIC
	$<INSTALL_INTERFACE:include>
	$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src>
)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

install(TARGETS quickfast
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

foreach (HEADER ${HEADERS})
	file(RELATIVE_PATH HEADER_REL ${PROJECT_SOURCE_DIR}/src ${PROJECT_SOURCE_DIR}/${HEADER})
	get_filename_component(HEADER_DIR ${HEADER_REL} DIRECTORY)
    install(FILES ${PROJECT_SOURCE_DIR}/${HEADER} DESTINATION include/quickfast/${HEADER_DIR})
endforeach()
