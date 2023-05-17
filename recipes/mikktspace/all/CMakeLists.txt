cmake_minimum_required(VERSION 3.4)
project(mikktspace LANGUAGES C)

add_library(mikktspace ${MIKKTSPACE_SRC_DIR}/mikktspace.c)
target_include_directories(mikktspace PUBLIC ${MIKKTSPACE_SRC_DIR})
set_target_properties(mikktspace PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(CheckFunctionExists)
check_function_exists(pow HAVE_MATH_SYSTEM)
if(NOT HAVE_MATH_SYSTEM)
    target_link_libraries(mikktspace PRIVATE m)
endif()

include(GNUInstallDirs)
install(TARGETS mikktspace
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${MIKKTSPACE_SRC_DIR}/mikktspace.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
