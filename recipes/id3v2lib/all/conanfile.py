from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.53.0"


class LibwebmConan(ConanFile):
    name = "id3v2lib"
    description = "id3v2lib is a library written in C to read and edit id3 tags from mp3 files."
    topics = ("conan", "id3", "tags", "mp3", "container", "media", "audio")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/larsbs/id3v2lib"
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "id3v2lib")
        self.cpp_info.set_property("cmake_target_name", "id3v2lib::id3v2lib")
        self.cpp_info.set_property("pkg_config_name", "id3v2lib")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["id3v2lib"].libs = ["id3v2lib"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "id3v2lib"
        self.cpp_info.names["cmake_find_package_multi"] = "id3v2lib"
        self.cpp_info.components["id3v2lib"].names["cmake_find_package"] = "id3v2lib"
        self.cpp_info.components["id3v2lib"].names["cmake_find_package_multi"] = "id3v2lib"
        self.cpp_info.components["id3v2lib"].set_property("cmake_target_name", "id3v2lib::id3v2lib")
        self.cpp_info.components["id3v2lib"].set_property("pkg_config_name", "id3v2lib")
