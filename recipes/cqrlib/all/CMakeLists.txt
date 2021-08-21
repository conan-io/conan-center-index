cmake_minimum_required(VERSION 3.4)
project(CQRlib C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(PROJECT_DIR ${CMAKE_CURRENT_LIST_DIR}/source_subfolder)

add_library(${PROJECT_NAME} ${PROJECT_DIR}/cqrlib.c)
target_include_directories(${PROJECT_NAME} PRIVATE ${PROJECT_DIR})
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)

find_library(M_LIB m)
if(M_LIB)
    target_link_libraries(${PROJECT_NAME} PRIVATE ${M_LIB})
endif()

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${PROJECT_DIR}/cqrlib.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
