cmake_minimum_required(VERSION 3.15)

project(runtimeqml LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)


find_package(Qt5 CONFIG)
find_package(Qt6 CONFIG)
if (Qt6_FOUND)
    set(Qt Qt6)
    set(HEADERS runtimeqml.hpp)
    add_library(${PROJECT_NAME} runtimeqml.hpp runtimeqml.cpp)
elseif(Qt5_FOUND)
    set(Qt Qt5)
    set(HEADERS runtimeqml.h)
    add_library(${PROJECT_NAME} runtimeqml.h runtimeqml.cpp)
else()
    message(FATAL_ERROR "Qt was not found")
endif()

target_link_libraries(${PROJECT_NAME} PUBLIC ${Qt}::Core ${Qt}::Quick ${Qt}::Widgets)
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}" C_VISIBILITY_PRESET hidden)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
