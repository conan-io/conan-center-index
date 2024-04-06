cmake_minimum_required(VERSION 3.15)

project(nmea LANGUAGES C)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_library(${PROJECT_NAME})

set(NMEA_INCLUDE_DIR ${NMEA_ROOT_DIR}/include)
set(NMEA_SRC_DIR ${NMEA_ROOT_DIR}/src)

target_sources(
    ${PROJECT_NAME}
    PRIVATE
	    ${NMEA_SRC_DIR}/context.c
		${NMEA_SRC_DIR}/generate.c
		${NMEA_SRC_DIR}/generator.c
		${NMEA_SRC_DIR}/gmath.c
		${NMEA_SRC_DIR}/info.c
		${NMEA_SRC_DIR}/parse.c
		${NMEA_SRC_DIR}/parser.c
		${NMEA_SRC_DIR}/sentence.c
		${NMEA_SRC_DIR}/time.c
		${NMEA_SRC_DIR}/tok.c
)

target_include_directories(
    ${PROJECT_NAME}
    PUBLIC
        ${NMEA_INCLUDE_DIR}
)

set(
	NMEA_HEADERS
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/config.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/context.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/generate.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/generator.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/gmath.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/info.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/nmea.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/parse.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/parser.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/sentence.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/time.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/tok.h
	${NMEA_INCLUDE_DIR}/${PROJECT_NAME}/units.h
)

set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES
        PUBLIC_HEADER "${NMEA_HEADERS}"
        C_EXTENSIONS OFF
)

find_library(LIBM m)
target_link_libraries(${PROJECT_NAME} PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

include(GNUInstallDirs)
install(
    TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}
)
