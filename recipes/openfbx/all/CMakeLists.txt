cmake_minimum_required(VERSION 3.8)
project(openfbx)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(${PROJECT_NAME} source_subfolder/src/ofbx.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
target_link_libraries(${PROJECT_NAME} PRIVATE ${CONAN_LIBS})

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES source_subfolder/src/ofbx.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
