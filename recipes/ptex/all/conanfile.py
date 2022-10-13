from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class PtexConan(ConanFile):
    name = "ptex"
    description = "Ptex is a texture mapping system developed by Walt Disney " \
                  "Animation Studios for production-quality rendering."
    license = "BSD-3-Clause"
    topics = ("ptex", "texture-mapping")
    homepage = "https://ptex.us"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PTEX_BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["PTEX_BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        cmake_target = "Ptex_dynamic" if self.options.shared else "Ptex_static"
        self.cpp_info.set_property("cmake_file_name", "ptex")
        self.cpp_info.set_property("cmake_target_name", "Ptex::{}".format(cmake_target))
        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["_ptex"].libs = ["Ptex"]
        if not self.options.shared:
            self.cpp_info.components["_ptex"].defines.append("PTEX_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_ptex"].system_libs.append("pthread")
        self.cpp_info.components["_ptex"].requires = ["zlib::zlib"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ptex"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ptex"
        self.cpp_info.names["cmake_find_package"] = "Ptex"
        self.cpp_info.names["cmake_find_package_multi"] = "Ptex"
        self.cpp_info.components["_ptex"].set_property("cmake_target_name", "Ptex::{}".format(cmake_target))
        self.cpp_info.components["_ptex"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_ptex"].names["cmake_find_package_multi"] = cmake_target
