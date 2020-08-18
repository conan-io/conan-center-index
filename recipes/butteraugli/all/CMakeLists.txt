cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

set(SRCS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/butteraugli/butteraugli.cc)
set(HDRS_FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/butteraugli/butteraugli.h)

add_library(butteraugli_lib ${SRCS_FILES} ${HDRS_FILES})
target_include_directories(butteraugli_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)
set_property(TARGET butteraugli_lib PROPERTY CXX_STANDARD 11)

install(TARGETS butteraugli_lib
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(FILES ${HDRS_FILES} DESTINATION include/butteraugli)
