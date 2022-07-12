cmake_minimum_required(VERSION 2.8.12)
project(SDL2_net C)

include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(SDL2 REQUIRED)

set(SOURCES 
  source_subfolder/SDLnet.c
  source_subfolder/SDLnetselect.c
  source_subfolder/SDLnetTCP.c
  source_subfolder/SDLnetUDP.c	
)

set(HEADERS
  source_subfolder/SDL_net.h
  source_subfolder/SDLnetsys.h
)

add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PRIVATE "source_subfolder")

target_link_libraries(${PROJECT_NAME} SDL2::SDL2)

if(WIN32)
  target_link_libraries(${PROJECT_NAME} ws2_32 iphlpapi)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES
    DEFINE_SYMBOL DLL_EXPORT
    PUBLIC_HEADER source_subfolder/SDL_net.h
)

install(TARGETS ${PROJECT_NAME}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/SDL2
)
