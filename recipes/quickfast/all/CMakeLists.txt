# based on: https://github.com/microsoft/vcpkg/blob/master/ports/quickfast/CMakeLists.txt

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

file(GLOB SOURCES
	source_subfolder/src/Application/*.cpp
	source_subfolder/src/Common/*.cpp
	source_subfolder/src/Codecs/*.cpp
	source_subfolder/src/Communication/*.cpp
	source_subfolder/src/Messages/*.cpp
)

file(GLOB HEADERS RELATIVE ${PROJECT_SOURCE_DIR}
	source_subfolder/src/Application/*.h
	source_subfolder/src/Common/*.h
	source_subfolder/src/Codecs/*.h
	source_subfolder/src/Communication/*.h
	source_subfolder/src/Messages/*.h
)

add_library(quickfast ${HEADERS} ${SOURCES})

if(BUILD_SHARED_LIBS)
	target_compile_definitions(quickfast PRIVATE -DQUICKFAST_BUILD_DLL)
else()
	target_compile_definitions(quickfast PUBLIC -DQUICKFAST_HAS_DLL=0)
endif()

target_compile_features(quickfast PUBLIC cxx_std_11)

target_include_directories(quickfast PUBLIC
	source_subfolder/src
)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

install(TARGETS quickfast
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

foreach (HEADER ${HEADERS})
	file(RELATIVE_PATH HEADER_REL ${PROJECT_SOURCE_DIR}/source_subfolder/src ${PROJECT_SOURCE_DIR}/${HEADER})
	get_filename_component(HEADER_DIR ${HEADER_REL} DIRECTORY)
    install(FILES ${HEADER} DESTINATION include/quickfast/${HEADER_DIR})
endforeach()
