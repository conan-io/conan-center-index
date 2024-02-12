cmake_minimum_required(VERSION 3.10...3.24)
project(google-cloud-cpp-test CXX)

find_package(google-cloud-cpp CONFIG REQUIRED)

# There are too many libraries to test them all. We
# should pick what we test with a view to detecting
# the most common packaging problems.

set(tests
    # Bigtable, Pub/Sub and Spanner have signficant amounts of
    # custom code and thus some amount of ad-hoc dependencies on
    # absl::* components.
    "bigtable" "pubsub" "spanner"
    # Storage has custom code and does not depend on gRPC or Protobuf.
    "storage"
    # Speech is a good model for most other libraries.
    "speech")
if (WITH_COMPUTE)
    # Compute does not use gRPC and has a different structure from most
    # libraries.
    list(APPEND tests "compute")
endif ()

foreach(component IN LISTS tests)
    add_executable("${component}" "${component}.cpp")
    target_compile_features("${component}" PRIVATE cxx_std_14)
    target_link_libraries("${component}" google-cloud-cpp::${component})
endforeach()
