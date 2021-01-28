cmake_minimum_required(VERSION 2.8.11)
project(wiringPi C)

include(conanbuildinfo.cmake)
conan_basic_setup()

FILE(GLOB SRC_FILES source_subfolder/wiringPi/*.c)
message(STATUS "SRC_FILES: ${SRC_FILES}")
if(NOT WITH_WPI_EXTENSIONS)
  list(FILTER SRC_FILES EXCLUDE REGEX ".*wpiExtensions.c")
  list(FILTER SRC_FILES EXCLUDE REGEX ".*drcNet.c")
endif()

add_library(${PROJECT_NAME} ${SRC_FILES})
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/wiringPi)
target_link_libraries(${PROJECT_NAME} PUBLIC ${CONAN_LIBS})

if(WITH_DEV_LIB)
    FILE(GLOB SRC_FILES source_subfolder/devLib//*.c)
    list(FILTER SRC_FILES EXCLUDE REGEX ".*piFaceOld.c")
    add_library(wiringPiDevLib ${SRC_FILES})
    target_include_directories(wiringPiDevLib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/devLib
                                                     ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/wiringPi)
endif()

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(DIRECTORY source_subfolder/wiringPi/ DESTINATION include
        FILES_MATCHING PATTERN "*.h")

if(WITH_DEV_LIB)

    install(TARGETS wiringPiDevLib
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

    install(DIRECTORY source_subfolder/devLib/ DESTINATION include
            FILES_MATCHING PATTERN "*.h")
endif()
