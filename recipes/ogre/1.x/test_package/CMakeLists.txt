cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)


find_package(OGRE ${OGRE_VERSION} COMPONENTS OgreMain REQUIRED)
add_executable(ogre_main ogre_main.cpp)
target_link_libraries(ogre_main
                        OGRE::OgreMain
                        )

set_target_properties(ogre_main PROPERTIES
CXX_STANDARD 17
CXX_STANDARD_REQUIRED ON
CXX_EXTENSIONS ON)

#if(WITH_BITES)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS Bites REQUIRED)
#    add_executable(bites_exe bites.cpp)
#    target_link_libraries(bites_exe PRIVATE OGRE::Bites)
#endif()
#
#if(WITH_MESHLODGENERATOR)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS MeshLodGenerator REQUIRED)
#    add_executable(meshloadgenerator_exe meshloadgenerator.cpp)
#    target_link_libraries(meshloadgenerator_exe PRIVATE OGRE::MeshLodGenerator)
#endif()
#
if(WITH_OVERLAY)
    find_package(OGRE ${OGRE_VERSION} COMPONENTS Overlay REQUIRED)
    add_executable(overlay_exe overlay.cpp)
    target_link_libraries(overlay_exe PRIVATE OGRE::Overlay)
endif()

##if(WITH_OVERLAY_IMGUI)
##    find_package(OGRE ${OGRE_VERSION} COMPONENTS Overlay REQUIRED)
##    add_executable(overlay_imgui_exe overlay_imgui.cpp)
##    target_link_libraries(overlay_imgui_exe PRIVATE OGRE::Overlay)
##endif()
#
#if(WITH_PAGING)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS Paging REQUIRED)
#    add_executable(paging_exe paging.cpp)
#    target_link_libraries(paging_exe PRIVATE OGRE::Paging)
#endif()
#
#if(WITH_PROPERTY)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS Property REQUIRED)
#    add_executable(property_exe property.cpp)
#    target_link_libraries(property_exe PRIVATE OGRE::Property)
#endif()
#
#if(WITH_HLMS)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS HLMS REQUIRED)
#    add_executable(hlms_exe hlms.cpp)
#    target_link_libraries(hlms_exe PRIVATE OGRE::HLMS)
#endif()
#
#if(WITH_RSHADERSYSTEM)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS RTShaderSystem REQUIRED)
#    add_executable(rtshadersystem_exe rtshadersystem.cpp)
#    target_link_libraries(rtshadersystem_exe PRIVATE OGRE::RTShaderSystem)
#endif()
#
#if(WITH_TERRAIN)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS Terrain REQUIRED)
#    add_executable(terrain_exe terrain.cpp)
#    target_link_libraries(terrain_exe PRIVATE OGRE::Terrain)
#endif()
#
#if(WITH_VOLUME)
#    find_package(OGRE ${OGRE_VERSION} COMPONENTS Volume REQUIRED)
#    add_executable(volume_exe volume.cpp)
#    target_link_libraries(volume_exe PRIVATE OGRE::Volume)
#endif()


#["WITH_PLUGIN_BSP"]
#["WITH_PLUGIN_SCENE"]
#["WITH_PLUGIN_OCTREE"]
#["WITH_PLUGIN_PCZ"]
#["WITH_PLUGIN_PFX"]
#["WITH_PLUGIN_STBI"]
