cmake_minimum_required(VERSION 3.4)
project(mikktspace)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(mikktspace ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mikktspace.c)
target_include_directories(mikktspace PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)
if(CMAKE_HOST_SYSTEM_NAME MATCHES "Linux")
    target_link_libraries(mikktspace PRIVATE m)
endif()

install(TARGETS mikktspace
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/mikktspace.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
