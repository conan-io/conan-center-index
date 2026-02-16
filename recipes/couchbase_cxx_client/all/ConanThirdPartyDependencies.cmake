# locate dependencies & realize alias targets from Conan
# Aliases provided by CMakeDeps; no manual ALIAS targets needed.

find_package(spdlog CONFIG QUIET)
find_package(Microsoft.GSL CONFIG QUIET)
find_package(Snappy CONFIG QUIET)
find_package(asio CONFIG QUIET)
find_package(hdr_histogram CONFIG QUIET)
find_package(llhttp CONFIG QUIET)
find_package(taocpp-json CONFIG QUIET)

# Copying the important part from the original cmake/ThirdPartyDependencies.cmake
set(CMAKE_POLICY_DEFAULT_CMP0063 NEW)

function(declare_system_library target)
  get_target_property(target_aliased_name ${target} ALIASED_TARGET)
  if(target_aliased_name)
    set(target ${target_aliased_name})
  endif()
  set_target_properties(${target} PROPERTIES INTERFACE_SYSTEM_INCLUDE_DIRECTORIES
                                             $<TARGET_PROPERTY:${target},INTERFACE_INCLUDE_DIRECTORIES>)
endfunction()

include(cmake/OpenSSL.cmake)

add_library(jsonsl OBJECT ${PROJECT_SOURCE_DIR}/third_party/jsonsl/jsonsl.c)
set_target_properties(jsonsl PROPERTIES C_VISIBILITY_PRESET hidden POSITION_INDEPENDENT_CODE TRUE)
target_include_directories(jsonsl SYSTEM PUBLIC ${PROJECT_SOURCE_DIR}/third_party/jsonsl)

declare_system_library(snappy)
declare_system_library(llhttp::llhttp)
declare_system_library(hdr_histogram_static)
declare_system_library(Microsoft.GSL::GSL)
declare_system_library(spdlog::spdlog)
declare_system_library(asio)
declare_system_library(taocpp::json)
