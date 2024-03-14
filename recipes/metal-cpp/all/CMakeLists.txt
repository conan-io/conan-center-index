cmake_minimum_required(VERSION 3.12)
project(metal-cpp)

option(HAS_METALFX "Is a version with MetalFX support (macOS >= 14/iOS >= 17)" Off)

add_library(metal-cpp src/implementation.cpp)
install(TARGETS  metal-cpp  DESTINATION  lib)
target_include_directories(metal-cpp  PRIVATE  src)

target_link_libraries(metal-cpp  PRIVATE  "-framework Foundation"
                                          "-framework Metal"
                                          "-framework MetalKit"
                                          "-framework QuartzCore")

# Copy the headers
install(DIRECTORY  src/Foundation  DESTINATION  include)
install(DIRECTORY  src/Metal  DESTINATION  include)
install(DIRECTORY  src/QuartzCore  DESTINATION  include)

# MetalFX is only available from metal-cpp for macOS >= 14/iOS >= 17
if(HAS_METALFX)
    target_compile_definitions(metal-cpp  PRIVATE  -DHAS_METALFX)
    target_link_libraries(metal-cpp  PRIVATE  "-framework MetalFX")
    install(DIRECTORY  src/MetalFX  DESTINATION  include)
endif()
