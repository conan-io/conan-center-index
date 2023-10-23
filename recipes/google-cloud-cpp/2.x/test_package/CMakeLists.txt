cmake_minimum_required(VERSION 3.10...3.24)
project(google-cloud-cpp-test CXX)

find_package(google-cloud-cpp CONFIG REQUIRED)

# There are too many libraries to test them all. We
# should pick what we test with a view to detecting
# the most common packaging problems.

# Bigtable, Pub/Sub and Spanner have signficant amounts of
# custom code and thus some amount of ad-hoc dependencies on
# absl::* components.
# Storage has custom code and does not depend on gRPC or Protobuf.
# Speech is a good model for most other libraries.
foreach(component IN ITEMS "bigtable" "pubsub" "spanner" "speech" "storage")
    add_executable("${component}" "${component}.cpp")
    target_compile_features("${component}" PRIVATE cxx_std_14)
    target_link_libraries("${component}" google-cloud-cpp::${component})
endforeach()
