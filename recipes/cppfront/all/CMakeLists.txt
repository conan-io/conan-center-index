cmake_minimum_required(VERSION 3.15)
project(cppfront CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# find_package(asio REQUIRED CONFIG)
# find_package(fmt REQUIRED CONFIG)

add_definitions(-DASIO_ENABLE_HANDLER_TRACKING)

add_executable(${PROJECT_NAME}
    source/cppfront.cpp
)

# target_include_directories(${PROJECT_NAME} PUBLIC
#   $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
#   $<INSTALL_INTERFACE:include>)

# if (TARGET fmt::fmt)
#     target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
# else()
#     target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt-header-only)
# endif()

# target_link_libraries(${PROJECT_NAME} PRIVATE asio::asio)

install(TARGETS ${PROJECT_NAME} DESTINATION "."
        RUNTIME DESTINATION bin
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        )



# cmake_minimum_required(VERSION 3.8)
# project(cppfront)

# set(CMAKE_CXX_STANDARD 20)
# set(CMAKE_CXX_STANDARD_REQUIRED ON)

# # include(conanbuildinfo.cmake)
# # conan_basic_setup()

# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup()

# add_executable(${PROJECT_NAME} source/cppfront.cpp)
