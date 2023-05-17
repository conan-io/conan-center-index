cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

file(GLOB SRCS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.cpp)
file(GLOB HDRS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.h)

add_library(rg_etc1 ${SRCS_FILES})
target_include_directories(rg_etc1 PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

install(TARGETS rg_etc1
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(FILES ${HDRS_FILES} DESTINATION include)
