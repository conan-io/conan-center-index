cmake_minimum_required(VERSION 3.15)

project(qtxlsxwriter)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

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

# TODO: remove when the qt recipe is fixed
# and this package is linked to the target for qt
target_include_directories(${PROJECT_NAME} PRIVATE ${CONAN_INCLUDE_DIRS})
target_link_directories(${PROJECT_NAME} PRIVATE ${CONAN_LIB_DIRS})
target_compile_definitions(${PROJECT_NAME} PRIVATE ${CONAN_DEFINES_QTXLSXWRITER})

# get the actual library file name of the Qt GUI module (for ex. it can be `Qt5Gui_debug`)
foreach(lib ${CONAN_LIBS})
    string(FIND ${lib} "Qt5Gui" qtgui_found)
    if(NOT (qtgui_found EQUAL -1))
        set(qtgui_name ${lib})
        break()
    endif()
endforeach()

# place qt::Gui before qt::Core (important for some toolchains)
# since the current qt recipe provides an incorrect order of libraries
# TODO: link to the target when the qt recipe is fixed
target_link_libraries(${QTXLSXWRITER_TARGET_NAME}
	${qtgui_name}
	${CONAN_LIBS}
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

file(GLOB QTXLSXWRITER_PRIVATE_HEADERS LIST_DIRECTORIES=false source_subfolder/src/xlsx/*_p.h)
set(QTXLSXWRITER_PUBLIC_HEADERS ${QTXLSXWRITER_HEADERS})
list(REMOVE_ITEM QTXLSXWRITER_PUBLIC_HEADERS ${QTXLSXWRITER_PRIVATE_HEADERS})
set_property(TARGET ${QTXLSXWRITER_TARGET_NAME} PROPERTY
	PUBLIC_HEADER ${QTXLSXWRITER_PUBLIC_HEADERS}
)

# define installing rules for target files
install(TARGETS ${QTXLSXWRITER_TARGET_NAME}
	PUBLIC_HEADER DESTINATION include
)

set_property(GLOBAL PROPERTY AUTOGEN_SOURCE_GROUP "Generated Files")
