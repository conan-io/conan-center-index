import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class LightPcapNgConan(ConanFile):
    name = "lightpcapng"
    description = "Library for general-purpose tracing based on PCAPNG file format"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Technica-Engineering/LightPcapNg"
    topics = ("pcapng", "pcap")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zstd": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.with_zstd:
            self.options["zstd"].shared = self.options.shared
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIGHT_USE_ZSTD"] = self.options.with_zstd
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "light_pcapng")
        self.cpp_info.set_property("cmake_target_name", "light_pcapng::light_pcapng")
        self.cpp_info.components["liblight_pcapng"].libs = ["light_pcapng"]
        if self.options.with_zstd:
            self.cpp_info.components["liblight_pcapng"].requires = ["zstd::zstd"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "light_pcapng"
        self.cpp_info.names["cmake_find_package_multi"] = "light_pcapng"
        self.cpp_info.components["liblight_pcapng"].names["cmake_find_package"] = "light_pcapng"
        self.cpp_info.components["liblight_pcapng"].names["cmake_find_package_multi"] = "light_pcapng"
