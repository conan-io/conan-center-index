# Based on https://github.com/kthohr/optim/blob/5453f48aca695e6fef123677f35cb4d22e356e73/configure
cmake_minimum_required(VERSION 3.15)
project(OptimLib LANGUAGES CXX)

set(OPTIM_LINEAR_ALG_LIB "eigen" CACHE STRING "Choice of linear algebra library")
set(OPTIM_FPN_TYPE  "double" CACHE STRING "Floating-point number type")
option(OPTIM_PARALLEL "Enable OpenMP parallelization features" ON)

file(GLOB_RECURSE SOURCES src/*.cpp)

add_library(optim ${SOURCES})
target_include_directories(optim PUBLIC include)
target_compile_features(optim PUBLIC cxx_std_11)

target_compile_options(optim PRIVATE -Wall)
if(NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(optim PRIVATE -O3 -ffp-contract=fast)
    target_compile_definitions(optim PRIVATE -DARMA_NO_DEBUG)
endif()

if(OPTIM_LINEAR_ALG_LIB STREQUAL "eigen")
    find_package(Eigen3 REQUIRED)
    target_link_libraries(optim PUBLIC Eigen3::Eigen)
    target_compile_definitions(optim PRIVATE -DOPTIM_ENABLE_EIGEN_WRAPPERS)
elseif(OPTIM_LINEAR_ALG_LIB STREQUAL "arma")
    find_package(Armadillo REQUIRED)
    target_link_libraries(optim PUBLIC Armadillo::Armadillo)
    target_compile_definitions(optim PRIVATE -DOPTIM_ENABLE_ARMA_WRAPPERS)
else()
    message(FATAL_ERROR "OPTIM_LINEAR_ALG_LIB must be either 'eigen' or 'arma'. Got: ${OPTIM_LINEAR_ALG_LIB}")
endif()

target_compile_definitions(optim PRIVATE -DOPTIM_FPN_TYPE=${OPTIM_FPN_TYPE})

if(OPTIM_PARALLEL)
    find_package(OpenMP REQUIRED)
    target_link_libraries(optim PUBLIC OpenMP::OpenMP_CXX)
endif()

include(GNUInstallDirs)
install(TARGETS optim
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp" PATTERN "*.ipp"
)
