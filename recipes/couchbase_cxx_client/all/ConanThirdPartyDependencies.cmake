# locate dependencies & realize alias targets from Conan
# Aliases provided by CMakeDeps; no manual ALIAS targets needed.

find_package(spdlog CONFIG QUIET)
find_package(Microsoft.GSL CONFIG QUIET)
find_package(Snappy CONFIG QUIET)
find_package(asio CONFIG QUIET)
find_package(hdr_histogram CONFIG QUIET)
find_package(llhttp CONFIG QUIET)
find_package(taocpp-json CONFIG QUIET)

# now that we've connected the conan dependencies, we can call
# couchbase's own file for further setup
include(cmake/ThirdPartyDependencies.cmake)
