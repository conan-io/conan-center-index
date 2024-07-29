# A wrapper for https://github.com/pytorch/pytorch/blob/v2.4.0/cmake/Dependencies.cmake

find_package(cpuinfo REQUIRED CONFIG)
find_package(fp16 REQUIRED CONFIG)
find_package(miniz REQUIRED CONFIG)

find_package(fmt REQUIRED CONFIG)
add_library(fmt-header-only INTERFACE)

find_package(httplib REQUIRED CONFIG)
link_libraries(httplib::httplib)

if(CONAN_LIBTORCH_USE_PTHREADPOOL)
    find_package(pthreadpool REQUIRED CONFIG)
    include_directories(${pthreadpool_INCLUDE_DIRS})
endif()

if(CONAN_LIBTORCH_USE_FLATBUFFERS)
    find_package(flatbuffers REQUIRED CONFIG)
endif()

if(CONAN_LIBTORCH_USE_SLEEF)
    find_package(sleef REQUIRED CONFIG)
endif()

if(USE_XNNPACK)
    find_package(xnnpack REQUIRED CONFIG)
    include_directories(${xnnpack_INCLUDE_DIRS})
endif()

if(USE_VULKAN)
    message(FATAL_ERROR "TODO: USE_VULKAN")
endif()

if(USE_FBGEMM)
    find_package(fbgemmLibrary REQUIRED CONFIG)
endif()

if(USE_PYTORCH_QNNPACK)
    find_package(fxdiv REQUIRED CONFIG)
    find_package(psimd REQUIRED CONFIG)
endif()

if(USE_MIMALLOC)
    find_package(mimalloc REQUIRED CONFIG)
endif()
