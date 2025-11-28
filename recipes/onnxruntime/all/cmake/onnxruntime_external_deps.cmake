# Replacement for https://github.com/microsoft/onnxruntime/blob/v1.23.2/cmake/external/onnxruntime_external_deps.cmake

if(NOT onnxruntime_DISABLE_ABSEIL)
  find_package(absl REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES abseil::abseil)
  include_directories(${absl_INCLUDE_DIRS})
  set(ABSEIL_LIBS abseil::abseil)
endif()

find_package(re2 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES re2::re2)

#flatbuffers 1.11.0 does not have flatbuffers::IsOutRange, therefore we require 1.12.0+
find_package(Flatbuffers REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES flatbuffers::flatbuffers)

find_package(Protobuf REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES protobuf::libprotobuf)
set(ONNX_CUSTOM_PROTOC_EXECUTABLE protoc)
set(PROTOC_EXECUTABLE protoc)

find_package(date REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES date::date)
include_directories(${date_INCLUDE_DIRS})
add_library(date_interface INTERFACE)

find_package(Boost REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Boost::mp11)

find_package(nlohmann_json REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES nlohmann_json::nlohmann_json)

find_package(cpuinfo REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES cpuinfo::cpuinfo)
if (TARGET cpuinfo::clog)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES cpuinfo::clog)
endif()
set(CPUINFO_SUPPORTED ${cpuinfo_FOUND})
if(CPUINFO_SUPPORTED)
  if (CMAKE_SYSTEM_NAME STREQUAL "iOS")
    set(IOS ON CACHE INTERNAL "")
    set(IOS_ARCH "${CMAKE_OSX_ARCHITECTURES}" CACHE INTERNAL "")
  endif()

  # if this is a wasm build with xnnpack (only type of wasm build where cpuinfo is involved)
  # we do not use cpuinfo in ORT code, so don't define CPUINFO_SUPPORTED.
  if (NOT CMAKE_SYSTEM_NAME STREQUAL "Emscripten")
    string(APPEND CMAKE_CXX_FLAGS " -DCPUINFO_SUPPORTED")
  endif()
endif()
if(TARGET cpuinfo::cpuinfo AND NOT TARGET cpuinfo)
  message(STATUS "Aliasing cpuinfo::cpuinfo to cpuinfo")
  add_library(cpuinfo ALIAS cpuinfo::cpuinfo)
endif()

if (NOT WIN32)
  find_package(nsync REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES nsync::nsync_cpp)
  include_directories(${nsync_INCLUDE_DIRS})
  add_library(nsync_cpp INTERFACE)
endif()

find_package(Microsoft.GSL 4.0 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Microsoft.GSL::GSL)
include_directories(${Microsoft.GSL_INCLUDE_DIRS})

find_package(safeint REQUIRED CONFIG)
include_directories(${safeint_INCLUDE_DIRS})
add_library(safeint_interface IMPORTED INTERFACE)

find_package(ONNX REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES onnx onnx_proto)

find_package(Eigen3 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Eigen3::Eigen)
set(eigen_INCLUDE_DIRS ${Eigen3_INCLUDE_DIRS})

if(WIN32)
  find_package(wil REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES WIL::WIL)
  include_directories(${wil_INCLUDE_DIRS})
endif()

# XNNPACK EP
if (onnxruntime_USE_XNNPACK)
  if (onnxruntime_DISABLE_CONTRIB_OPS)
    message(FATAL_ERROR "XNNPACK EP requires the internal NHWC contrib ops to be available "
                         "but onnxruntime_DISABLE_CONTRIB_OPS is ON")
  endif()
  find_package(xnnpack REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES xnnpack::xnnpack)
  add_library(XNNPACK INTERFACE)
endif()

if (onnxruntime_USE_MIMALLOC)
  find_package(mimalloc REQUIRED CONFIG)
  add_definitions(-DUSE_MIMALLOC)
endif()

file(TO_NATIVE_PATH ${CMAKE_BINARY_DIR}  ORT_BINARY_DIR)
file(TO_NATIVE_PATH ${PROJECT_SOURCE_DIR}  ORT_SOURCE_DIR)
