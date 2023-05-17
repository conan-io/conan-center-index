cmake_minimum_required(VERSION 2.8.11)
project(wiringPi C)

file(GLOB SRC_FILES ${WIRINGPI_SRC_DIR}/wiringPi/*.c)

message(STATUS "SRC_FILES: ${SRC_FILES}")
if(NOT WIRINGPI_WITH_WPI_EXTENSIONS)
  list(FILTER SRC_FILES EXCLUDE REGEX ".*wpiExtensions.c")
  list(FILTER SRC_FILES EXCLUDE REGEX ".*drcNet.c")
endif()

add_library(${PROJECT_NAME} ${SRC_FILES})
target_include_directories(${PROJECT_NAME} PUBLIC ${WIRINGPI_SRC_DIR}/wiringPi)

if(WIRINGPI_WITH_DEV_LIB)
    file(GLOB SRC_FILES ${WIRINGPI_SRC_DIR}/devLib/*.c)
    list(FILTER SRC_FILES EXCLUDE REGEX ".*piFaceOld.c")
    add_library(wiringPiDevLib ${SRC_FILES})
    target_include_directories(wiringPiDevLib PUBLIC ${WIRINGPI_SRC_DIR}/devLib
                                                     ${WIRINGPI_SRC_DIR}/wiringPi)
endif()

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(DIRECTORY ${WIRINGPI_SRC_DIR}/wiringPi/ DESTINATION include
        FILES_MATCHING PATTERN "*.h")

if(WIRINGPI_WITH_DEV_LIB)

    install(TARGETS wiringPiDevLib
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

    install(DIRECTORY ${WIRINGPI_SRC_DIR}/devLib/ DESTINATION include
            FILES_MATCHING PATTERN "*.h")
endif()
