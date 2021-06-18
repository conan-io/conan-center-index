cmake_minimum_required(VERSION 3.4)
project(tiny-regex-c C)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(${PROJECT_NAME} source_subfolder/re.c)
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
if(RE_DOT_MATCHES_NEWLINE)
    target_compile_definitions(${PROJECT_NAME} PUBLIC RE_DOT_MATCHES_NEWLINE=1)
else()
    target_compile_definitions(${PROJECT_NAME} PUBLIC RE_DOT_MATCHES_NEWLINE=0)
endif()

include(GNUInstallDirs)
install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES source_subfolder/re.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
