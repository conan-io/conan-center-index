from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=1.52.0"


class RecastNavigationConan(ConanFile):
    name = "recastnavigation"
    homepage = "https://github.com/recastnavigation/recastnavigation"
    description = " Navigation-mesh Toolset for Games"
    topics = ("navmesh", "recast", "navigation", "crowd")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Zlib"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RECASTNAVIGATION_DEMO"] = False
        tc.variables["RECASTNAVIGATION_TESTS"] = False
        tc.variables["RECASTNAVIGATION_EXAMPLES"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "recastnavigation")
        self.cpp_info.set_property("pkg_config_name", "recastnavigation")

        self.cpp_info.components["Recast"].set_property("cmake_target_name", "RecastNavigation::Recast")
        self.cpp_info.components["Recast"].libs = ["Recast"]

        self.cpp_info.components["Detour"].set_property("cmake_target_name", "RecastNavigation::Detour")
        self.cpp_info.components["Detour"].libs = ["Detour"]

        self.cpp_info.components["DetourCrowd"].set_property("cmake_target_name", "RecastNavigation::DetourCrowd")
        self.cpp_info.components["DetourCrowd"].libs = ["DetourCrowd"]
        self.cpp_info.components["DetourCrowd"].requires = ["Detour"]

        self.cpp_info.components["DetourTileCache"].set_property("cmake_target_name", "RecastNavigation::DetourTileCache")
        self.cpp_info.components["DetourTileCache"].libs = ["DetourTileCache"]
        self.cpp_info.components["DetourTileCache"].requires = ["Detour"]

        self.cpp_info.components["DebugUtils"].set_property("cmake_target_name", "RecastNavigation::DebugUtils")
        self.cpp_info.components["DebugUtils"].libs = ["DebugUtils"]
        self.cpp_info.components["DebugUtils"].requires = ["Recast", "Detour", "DetourTileCache"]

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "recastnavigation"
        self.cpp_info.filenames["cmake_find_package_multi"] = "recastnavigation"
        self.cpp_info.names["cmake_find_package"] = "RecastNavigation"
        self.cpp_info.names["cmake_find_package_multi"] = "RecastNavigation"
        self.cpp_info.components["Recast"].names["cmake_find_package"] = "Recast"
        self.cpp_info.components["Recast"].names["cmake_find_package_multi"] = "Recast"
        self.cpp_info.components["Detour"].names["cmake_find_package"] = "Detour"
        self.cpp_info.components["Detour"].names["cmake_find_package_multi"] = "Detour"
        self.cpp_info.components["DetourCrowd"].names["cmake_find_package"] = "DetourCrowd"
        self.cpp_info.components["DetourCrowd"].names["cmake_find_package_multi"] = "DetourCrowd"
        self.cpp_info.components["DetourTileCache"].names["cmake_find_package"] = "DetourTileCache"
        self.cpp_info.components["DetourTileCache"].names["cmake_find_package_multi"] = "DetourTileCache"
        self.cpp_info.components["DebugUtils"].names["cmake_find_package"] = "DebugUtils"
        self.cpp_info.components["DebugUtils"].names["cmake_find_package_multi"] = "DebugUtils"
