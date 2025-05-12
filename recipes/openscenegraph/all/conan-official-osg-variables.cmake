# Reproduce https://github.com/openscenegraph/OpenSceneGraph/blob/master/packaging/cmake/OpenSceneGraphConfig.cmake.in
# Component-specific variables are not created. Use the component targets instead.

# Only export these for the OpenSceneGraph config file, not FindOSG.cmake
if(NOT DEFINED OSG_LIBRARIES)
    set(OPENSCENEGRAPH_FOUND TRUE)
    set(OPENSCENEGRAPH_LIBRARIES ${OpenSceneGraph_LIBRARIES})
    set(OPENSCENEGRAPH_INCLUDE_DIR ${OpenSceneGraph_INCLUDE_DIRS})
    set(OPENSCENEGRAPH_INCLUDE_DIRS ${OpenSceneGraph_INCLUDE_DIRS})

    set(OPENSCENEGRAPH_VERSION ${OpenSceneGraph_VERSION})
    set(OPENSCENEGRAPH_VERSION_STRING ${OpenSceneGraph_VERSION_STRING})

    set(OSG_LIBRARY ${OpenSceneGraph_LIBRARIES})
    set(OSG_LIBRARIES ${OpenSceneGraph_LIBRARIES})
    set(OSG_INCLUDE_DIR ${OpenSceneGraph_INCLUDE_DIRS})
    set(OSG_INCLUDE_DIRS ${OpenSceneGraph_INCLUDE_DIRS})
endif()

# Reproduce https://github.com/openscenegraph/OpenSceneGraph/blob/master/CMakeModules/FindOpenThreads.cmake
set(OPENTHREADS_FOUND TRUE)
set(OPENTHREADS_INCLUDE_DIR ${OpenSceneGraph_INCLUDE_DIRS})
set(OPENTHREADS_LIBRARY OpenThreads::OpenThreads)
