cmake_minimum_required(VERSION 3.16)

project(log.c 
	    VERSION 0.1.0 
	    DESCRIPTION "A simple logging library implemented in C99" 
	    HOMEPAGE_URL "https://github.com/rxi/log.c"
	    LANGUAGES C
	)

# Init Conan stuff
include(conanbuildinfo.cmake)
conan_basic_setup()

# Set paths
include(GNUInstallDirs)
set(SRC_FOLDER "source_subfolder")

# Library files SHARED or STATIC set by Conan with BUILD_SHARED_LIBS
add_library(${PROJECT_NAME} ${SRC_FOLDER}/src/log.c ${SRC_FOLDER}/src/log.h)

# Library info
set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION})

# Conan options
if (${LOG_USE_COLOR})
    TARGET_COMPILE_DEFINITIONS(${PROJECT_NAME} PRIVATE LOG_USE_COLOR)
    message(STATUS "LOG_USE_COLOR")
endif()

if(UNIX OR MINGW)
    install(FILES ${SRC_FOLDER}/src/log.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
    install(FILES ${SRC_FOLDER}/LICENSE DESTINATION ${CMAKE_INSTALL_PREFIX}/licenses)
    install(TARGETS ${PROJECT_NAME}
	LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
	ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
endif()
    
if(MSVC)
  install(FILES ${SRC_FOLDER}/src/log.h DESTINATION include)
  install(FILES ${SRC_FOLDER}/LICENSE DESTINATION ${CMAKE_INSTALL_PREFIX}/licenses)
  install(TARGETS ${PROJECT_NAME}
          RUNTIME DESTINATION bin
          ARCHIVE DESTINATION lib)
endif()

message(STATUS "summary of build options:
    Install prefix:  ${CMAKE_INSTALL_PREFIX}
    Target system:   ${CMAKE_SYSTEM_NAME}
	Build shared lib:    ${BUILD_SHARED_LIBS}
    Compiler:
      C compiler:    ${CMAKE_C_COMPILER}
      CFLAGS:        ${CMAKE_C_FLAGS_${_build_type}} ${CMAKE_C_FLAGS}
")

