cmake_minimum_required(VERSION 3.10)
project(google-cloud-cpp-test CXX)

find_package(google-cloud-cpp CONFIG REQUIRED)

# There are too many libraries to test them all. We
# should pick what we test with a view to detecting
# the most common packaging problems.

# Bigtable, Pub/Sub and Spanner have signficant amounts of
# custom code and thus some amount of ad-hoc dependencies on
# absl::* components.
foreach(component IN ITEMS "bigtable" "pubsub" "spanner")
    add_executable("${component}" "${component}.cpp")
    target_link_libraries("${component}" google-cloud-cpp::${component})
endforeach()

# `google-cloud-cpp::storage` does not depend on gRPC,
# and have dependencies that no other component in
# `google-cloud-cpp` has, such as crc32c and libcurl.
add_executable(storage storage.cpp)
target_link_libraries(storage google-cloud-cpp::storage)

# The remaining 80+ components are fairly standarized in
# their packaging, but we should test at least one.
add_executable(speech speech.cpp)
target_link_libraries(speech google-cloud-cpp::speech)
