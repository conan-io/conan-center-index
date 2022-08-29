from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools import files
from conan import ConanFile
import os

required_conan_version = ">=1.45.0"


class Tixi3Conan(ConanFile):
    name = "tixi3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A simple xml interface based on libxml2 and libxslt"
    topics = ("tixi3", "xml")
    homepage = "https://github.com/DLR-SC/tixi"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def requirements(self):
        self.requires("libxml2/2.9.14")
        self.requires("libxslt/1.1.34")
        self.requires("libcurl/7.84.0")

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        # tixi is a c library
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"], src=self.recipe_folder, dst=self.export_sources_folder)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.export_sources_folder)

    def _patch_source(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, patch_file=patch["patch_file"])

    def build(self):
        self._patch_source()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # remove package generated cmake config files
        files.rmdir(self, 
            os.path.join(self.package_folder, "lib", "tixi3"))

        # copy the LICENSE file
        self.copy("LICENSE", dst="licenses", src=self.export_sources_folder)

        # remove share directory, which only contains documentation,
        # expamples...
        files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "tixi3"))
        self.cpp_info.libs = ['tixi3']

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ['Shlwapi']

        self.cpp_info.set_property("cmake_file_name", "tixi3")
        self.cpp_info.set_property("cmake_target_name", "tixi3")
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']
