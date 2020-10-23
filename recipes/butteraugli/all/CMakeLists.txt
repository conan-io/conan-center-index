cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif(WIN32 AND BUILD_SHARED_LIBS)

set(butteraugli_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)

set(SRCS_FILES ${butteraugli_DIR}/butteraugli/butteraugli.cc)
set(HDRS_FILES ${butteraugli_DIR}/butteraugli/butteraugli.h)
add_library(butteraugli_lib ${SRCS_FILES} ${HDRS_FILES})
target_include_directories(butteraugli_lib PUBLIC ${butteraugli_DIR})
set_property(TARGET butteraugli_lib PROPERTY CXX_STANDARD 11)

find_package(JPEG REQUIRED)
find_package(PNG REQUIRED)

add_library(butteraugli ${butteraugli_DIR}/butteraugli/butteraugli_main.cc)
target_link_libraries(butteraugli butteraugli_lib ${JPEG_LIBRARIES} ${PNG_LIBRARIES})
set_property(TARGET butteraugli PROPERTY CXX_STANDARD 11)

install(TARGETS butteraugli butteraugli_lib
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${HDRS_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/butteraugli)
