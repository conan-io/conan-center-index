cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper)

# The cmake_wrapper allows users to build only modules they want and not the entire sdk,
# the CMakeLists.txt from source does not provide this modularity to users (it's all or nothing).

foreach(sdk ${BUILD_LIST})
    if(${sdk} STREQUAL azure-core)
        # Always build Core
        add_subdirectory("src/sdk/core")
    elseif(${sdk} STREQUAL azure-storage-common)
        add_subdirectory("src/sdk/storage/azure-storage-common")
    elseif(${sdk} STREQUAL azure-storage-blobs)
        add_subdirectory("src/sdk/storage/azure-storage-blobs")
    elseif(${sdk} STREQUAL azure-storage-files-shares)
        add_subdirectory("src/sdk/storage/azure-storage-files-shares")
    endif()
endforeach()
