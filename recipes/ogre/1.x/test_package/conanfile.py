from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OGRE_VERSION"] = tools.Version(self.deps_cpp_info["ogre"].version)
        cmake.definitions["WITH_BITES"] = self.options["ogre"].OGRE_BUILD_COMPONENT_BITES
        cmake.definitions["WITH_MESHLODGENERATOR"] = self.options["ogre"].OGRE_BUILD_COMPONENT_MESHLODGENERATOR
        cmake.definitions["WITH_OVERLAY"] = self.options["ogre"].OGRE_BUILD_COMPONENT_OVERLAY
        cmake.definitions["WITH_OVERLAY_IMGUI"] = self.options["ogre"].OGRE_BUILD_COMPONENT_OVERLAY_IMGUI
        cmake.definitions["WITH_PAGING"] = self.options["ogre"].OGRE_BUILD_COMPONENT_PAGING
        cmake.definitions["WITH_PROPERTY"] = self.options["ogre"].OGRE_BUILD_COMPONENT_PROPERTY
        cmake.definitions["WITH_HLMS"] = self.options["ogre"].OGRE_BUILD_COMPONENT_HLMS
        cmake.definitions["WITH_RSHADERSYSTEM"] = self.options["ogre"].OGRE_BUILD_COMPONENT_RTSHADERSYSTEM
        cmake.definitions["WITH_TERRAIN"] = self.options["ogre"].OGRE_BUILD_COMPONENT_TERRAIN
        cmake.definitions["WITH_VOLUME"] = self.options["ogre"].OGRE_BUILD_COMPONENT_VOLUME
        cmake.definitions["WITH_PLUGIN_BSP"] = self.options["ogre"].OGRE_BUILD_PLUGIN_BSP
        cmake.definitions["WITH_PLUGIN_DOT_SCENE"] = self.options["ogre"].OGRE_BUILD_PLUGIN_DOT_SCENE
        cmake.definitions["WITH_PLUGIN_OCTREE"] = self.options["ogre"].OGRE_BUILD_PLUGIN_OCTREE
        cmake.definitions["WITH_PLUGIN_PCZ"] = self.options["ogre"].OGRE_BUILD_PLUGIN_PCZ
        cmake.definitions["WITH_PLUGIN_PFX"] = self.options["ogre"].OGRE_BUILD_PLUGIN_PFX
        cmake.definitions["WITH_PLUGIN_STBI"] = self.options["ogre"].OGRE_BUILD_PLUGIN_STBI
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
            
        ogre_main_bin_path = os.path.join("bin", "ogre_main")
        self.run(ogre_main_bin_path, run_environment=True)
