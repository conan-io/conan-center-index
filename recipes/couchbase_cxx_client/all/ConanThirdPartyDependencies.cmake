# locate dependencies & realize alias targets from Conan
# Aliases provided by CMakeDeps; no manual ALIAS targets needed.

find_package(spdlog CONFIG QUIET)
find_package(fmt CONFIG QUIET)
find_package(Microsoft.GSL CONFIG QUIET)
find_package(Snappy CONFIG QUIET)
find_package(asio CONFIG QUIET)
find_package(hdr_histogram CONFIG QUIET)
find_package(llhttp CONFIG QUIET)
find_package(taocpp-json CONFIG QUIET)

# Copying the important part from the original cmake/ThirdPartyDependencies.cmake
set(CMAKE_POLICY_DEFAULT_CMP0063 NEW)

include(cmake/OpenSSL.cmake)

add_library(jsonsl OBJECT ${PROJECT_SOURCE_DIR}/third_party/jsonsl/jsonsl.c)
set_target_properties(jsonsl PROPERTIES C_VISIBILITY_PRESET hidden POSITION_INDEPENDENT_CODE TRUE)
target_include_directories(jsonsl SYSTEM PUBLIC ${PROJECT_SOURCE_DIR}/third_party/jsonsl)
