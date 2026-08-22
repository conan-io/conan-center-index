cmake_minimum_required(VERSION 3.15)
project(quickfast CXX)

find_package(Boost REQUIRED CONFIG)
find_package(XercesC REQUIRED CONFIG)

file(GLOB SOURCES
    src/Application/*.cpp
    src/Common/*.cpp
    src/Codecs/*.cpp
    src/Communication/*.cpp
    src/Messages/*.cpp
)

file(GLOB HEADERS
    src/Application/*.h
    src/Common/*.h
    src/Codecs/*.h
    src/Communication/*.h
    src/Messages/*.h
)

add_library(quickfast ${HEADERS} ${SOURCES})

# Needed to keep support for deprecated placeholders in boost::bind
target_compile_definitions(quickfast PRIVATE -DBOOST_BIND_GLOBAL_PLACEHOLDERS)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(quickfast PUBLIC QUICKFAST_BUILD_DLL)
else()
    target_compile_definitions(quickfast PUBLIC QUICKFAST_HAS_DLL=0)
endif()

target_compile_features(quickfast PUBLIC cxx_std_11)
target_include_directories(quickfast PRIVATE src)
target_link_libraries(${PROJECT_NAME}
    Boost::boost
    Boost::thread
    Boost::system
    Boost::filesystem
    XercesC::XercesC
)
set_target_properties(quickfast PROPERTIES
    PUBLIC_HEADER "${HEADERS}"
)

install(TARGETS quickfast
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}
)

foreach (HEADER ${HEADERS})
    file(RELATIVE_PATH HEADER_REL ${PROJECT_SOURCE_DIR}/src ${HEADER})
    get_filename_component(HEADER_DIR ${HEADER_REL} DIRECTORY)
    install(FILES ${HEADER} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME}/${HEADER_DIR})
endforeach()
