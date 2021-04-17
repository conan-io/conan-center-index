cmake_minimum_required (VERSION 3.4.0)
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "Minimum OS X deployment version")
project (libplist)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include_directories(${PROJECT_SOURCE_DIR}/source_subfolder/src)
include_directories(${PROJECT_SOURCE_DIR}/source_subfolder/include)
include_directories(${PROJECT_SOURCE_DIR}/source_subfolder/libcnary)
include_directories(${PROJECT_SOURCE_DIR}/source_subfolder/libcnary/include)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
    add_definitions (-D_SCL_SECURE_NO_WARNINGS=1)
    add_definitions (-D_CRT_SECURE_NO_WARNINGS=1)

    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    set(CMAKE_VS_INCLUDE_INSTALL_TO_DEFAULT_BUILD 1)
endif()


#######################################################################
#                              libcnary                               #
#######################################################################

aux_source_directory(${PROJECT_SOURCE_DIR}/source_subfolder/libcnary CNARY_SRC)

add_library(cnary ${CNARY_SRC})

INSTALL(TARGETS cnary
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

#######################################################################
#                              libplist                               #
#######################################################################

aux_source_directory(${PROJECT_SOURCE_DIR}/source_subfolder/src SRC)

file(GLOB_RECURSE HEADERS "source_subfolder/include/*.h")

add_library(plist ${SRC})

target_link_libraries(plist cnary)

INSTALL(TARGETS plist
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

INSTALL(FILES ${HEADERS} DESTINATION include/plist)
