cmake_minimum_required(VERSION 3.15)

project(qtxlsxwriter)

find_package(qt REQUIRED CONFIG)

set(QTXLSXWRITER_TARGET_NAME qtxlsxwriter)

include(conan_qt_executables_variables)
set(CMAKE_AUTOMOC ON)

file(GLOB QTXLSXWRITER_HEADERS LIST_DIRECTORIES=false source_subfolder/src/xlsx/*.h)
file(GLOB QTXLSXWRITER_SOURCES LIST_DIRECTORIES=false source_subfolder/src/xlsx/*.cpp)

add_library(${QTXLSXWRITER_TARGET_NAME}
	${QTXLSXWRITER_HEADERS}
	${QTXLSXWRITER_SOURCES}
)

set(QT_VERSION "${QT_VERSION_MAJOR}.${QT_VERSION_MINOR}.${QT_VERSION_PATCH}")
target_include_directories(${QTXLSXWRITER_TARGET_NAME}
	PRIVATE
		$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/xlsx>
		# qtxlsxwriter uses qt private headers
		$<BUILD_INTERFACE:${QT_ROOT}/include/QtCore/${QT_VERSION}>
		$<BUILD_INTERFACE:${QT_ROOT}/include/QtGui/${QT_VERSION}>
		$<BUILD_INTERFACE:${QT_ROOT}/include/QtGui/${QT_VERSION}/QtGui>
	INTERFACE
		$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/src/xlsx>
		$<INSTALL_INTERFACE:include>
)

target_compile_features(${QTXLSXWRITER_TARGET_NAME}
	PRIVATE
		cxx_range_for
)

# place qt::Gui before qt::Core (important for some toolchains)
# since the current qt recipe provides an incorrect order of libraries
target_link_libraries(${QTXLSXWRITER_TARGET_NAME}
	$<$<TARGET_EXISTS:CONAN_LIB::qt_Qt5Gui_RELEASE>:CONAN_LIB::qt_Qt5Gui_RELEASE>
	$<$<TARGET_EXISTS:CONAN_LIB::qt_Qt5Gui_DEBUG>:CONAN_LIB::qt_Qt5Gui_DEBUG>
	$<$<TARGET_EXISTS:CONAN_LIB::qt_Qt5Gui_RELWITHDEBINFO>:CONAN_LIB::qt_Qt5Gui_RELWITHDEBINFO>
	$<$<TARGET_EXISTS:CONAN_LIB::qt_Qt5Gui_MINSIZEREL>:CONAN_LIB::qt_Qt5Gui_MINSIZEREL>
)

target_link_libraries(${QTXLSXWRITER_TARGET_NAME}
	qt::qt
)

get_target_property(target_type ${QTXLSXWRITER_TARGET_NAME} TYPE)
if (target_type STREQUAL "STATIC_LIBRARY")
	target_compile_definitions(${QTXLSXWRITER_TARGET_NAME}
		PUBLIC
			QTXLSX_STATIC
	)
endif()

set_target_properties(${QTXLSXWRITER_TARGET_NAME} PROPERTIES
	DEFINE_SYMBOL QT_BUILD_XLSX_LIB
)

set_property(TARGET ${QTXLSXWRITER_TARGET_NAME} PROPERTY PUBLIC_HEADER
	source_subfolder/src/xlsx/xlsxabstractooxmlfile.h
	source_subfolder/src/xlsx/xlsxabstractsheet.h
	source_subfolder/src/xlsx/xlsxcell.h
	source_subfolder/src/xlsx/xlsxcellformula.h
	source_subfolder/src/xlsx/xlsxcellrange.h
	source_subfolder/src/xlsx/xlsxcellreference.h
	source_subfolder/src/xlsx/xlsxchart.h
	source_subfolder/src/xlsx/xlsxchartsheet.h
	source_subfolder/src/xlsx/xlsxconditionalformatting.h
	source_subfolder/src/xlsx/xlsxdatavalidation.h
	source_subfolder/src/xlsx/xlsxdocument.h
	source_subfolder/src/xlsx/xlsxformat.h
	source_subfolder/src/xlsx/xlsxglobal.h
	source_subfolder/src/xlsx/xlsxrichstring.h
	source_subfolder/src/xlsx/xlsxworkbook.h
	source_subfolder/src/xlsx/xlsxworksheet.h
)

# define installing rules for target files
install(TARGETS ${QTXLSXWRITER_TARGET_NAME}
	PUBLIC_HEADER DESTINATION include
)

set_property(GLOBAL PROPERTY AUTOGEN_SOURCE_GROUP "Generated Files")
