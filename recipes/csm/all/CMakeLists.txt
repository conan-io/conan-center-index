cmake_minimum_required(VERSION 3.1)
project(csm LANGUAGES CXX)

find_package(Threads REQUIRED)
include(CheckFunctionExists)
check_function_exists(pow HAVE_MATH_SYSTEM)

file(GLOB CSM_SRCS ${CSM_SRC_DIR}/*.cpp)
add_library(csmapi SHARED ${CSM_SRCS})
target_include_directories(csmapi PRIVATE ${CSM_SRC_DIR})
target_link_libraries(csmapi PRIVATE Threads::Threads ${CMAKE_DL_LIBS})
if(NOT HAVE_MATH_SYSTEM)
    target_link_libraries(csmapi PRIVATE m)
endif()
set_target_properties(csmapi PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN TRUE
    VERSION ${CSM_VERSION}
    SOVERSION ${CSM_MAJOR_VERSION}
)
if(NOT WIN32)
    set_target_properties(csmapi PROPERTIES DEFINE_SYMBOL LINUX_BUILD)
endif()

include(GNUInstallDirs)
file(GLOB CSM_HEADERS ${CSM_SRC_DIR}/*.h)
install(FILES ${CSM_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/csm)
install(
    TARGETS csmapi
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
