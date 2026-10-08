from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0.9"

class DanceRudimentsConan(ConanFile):
    name = "dancerudiments"
    description = "Deterministic rhythmic positions. https://kieransimkin.co.uk/danceflow/"
    license = "MIT", "BSD-3-Clause", "CC0-1.0", "CC-BY-4.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://kieransimkin.co.uk/danceflow/"
    topics = "rhythm", "animation", "motion", "music"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        for option in ("TESTS", "PYTHON", "WASM", "C_ABI", "DEMO_TOOLS"):
            toolchain.cache_variables["DANCERUDIMENTS_BUILD_" + option] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        for source, target, filename in [("", "", "LICENSE"),
              ("collections/initial", "initial", "THIRD_PARTY_NOTICES.md"),
              ("collections/initial/sources/d3-ease", "d3-ease", "LICENSE"),
              ("python/dancerudiments_authoring/packs", "authoring", "THIRD_PARTY_NOTICES.md")]:
            copy(self, filename, os.path.join(self.source_folder, source),
                 os.path.join(self.package_folder, "licenses", target))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["DanceRudimentsCore" if self.settings.os == "Windows" else "DanceRudiments"]
        self.cpp_info.set_property("cmake_file_name", "DanceRudiments")
        self.cpp_info.set_property("cmake_target_name", "DanceRudiments::DanceRudiments")
