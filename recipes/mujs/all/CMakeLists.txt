cmake_minimum_required(VERSION 3.4)
project(mujs C)

include(conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB MUJS_SRC source_subfolder/js*.c source_subfolder/utf*.c source_subfolder/regexp.c)

add_library(${PROJECT_NAME} ${MUJS_SRC})
set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

find_library(M_LIB m)
if(M_LIB)
    target_link_libraries(${PROJECT_NAME} PRIVATE ${M_LIB})
endif()

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/mujs.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
