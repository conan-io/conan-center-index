import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.4"


class LibId3TagConan(ConanFile):
    name = "libid3tag"
    description = "ID3 tag manipulation library."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/tenacityteam/libid3tag/"
    topics = ("mad", "id3", "mp3", "MPEG", "audio", "decoder")
    generators = "CMakeDeps", "CMakeToolchain"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ["COPYRIGHT", "COPYING", "CREDITS"]:
            copy(self, license_file, self.source_folder, os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["id3tag"]

        if Version(self.version) >= "0.16":
            # These are the actual upstream target names
            # However older versions of the recipe did not reflect these -
            # So ensure only newly published versions use these target names, to prevent breakages
            # (consumers still have to update when they move to using a new version)
            self.cpp_info.set_property("cmake_file_name", "id3tag")
            self.cpp_info.set_property("cmake_target_name", "id3tag::id3tag")
            self.cpp_info.set_property("pkg_config_name", "id3tag")
