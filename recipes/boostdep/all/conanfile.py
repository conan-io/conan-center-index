import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, download, get

required_conan_version = ">=1.52.0"


class BoostDepConan(ConanFile):
    name = "boostdep"
    description = "A tool to create Boost module dependency reports"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/boostorg/boostdep"
    topics = ("dependency", "tree")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"boost/{self.version}")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        sources_info, license_info = self.conan_data["sources"][self.version]
        get(self, **sources_info, strip_root=True)
        download(self, **license_info, filename=os.path.basename(license_info["url"]))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
