cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(AzureSDK CONFIG REQUIRED)

add_executable(test_azure-core test_azure-core.cc)
target_link_libraries(test_azure-core PRIVATE Azure::azure-core)

add_executable(test_azure-storage-common test_azure-storage-common.cc)
target_link_libraries(test_azure-storage-common PRIVATE Azure::azure-core Azure::azure-storage-common)

add_executable(test_azure-storage-blobs test_azure-storage-blobs.cc)
target_link_libraries(test_azure-storage-blobs PRIVATE Azure::azure-core Azure::azure-storage-common Azure::azure-storage-blobs)

add_executable(test_azure-storage-files-shares test_azure-storage-files-shares.cc)
target_link_libraries(test_azure-storage-files-shares PRIVATE Azure::azure-core Azure::azure-storage-common Azure::azure-storage-files-shares)
