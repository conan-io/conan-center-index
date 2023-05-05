cmake_minimum_required(VERSION 3.12)
project(cppfront LANGUAGES CXX)

add_executable(${PROJECT_NAME} ${CPPFRONT_SRC_DIR}/source/cppfront.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY ${CPPFRONT_SRC_DIR}/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
