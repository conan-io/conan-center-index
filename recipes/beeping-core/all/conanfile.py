from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.6"


class BeepingCoreConan(ConanFile):
    name = "beeping-core"
    description = "C++20 library for encoding and decoding data over sound"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/beeping-io/beeping-core"
    topics = ("audio", "dsp", "data-over-sound", "fsk", "sound", "encoding")
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
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "15",
            "clang": "16",
            "gcc": "13",
            "msvc": "193",
            "Visual Studio": "17",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("spdlog/1.15.3")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise Exception(
                f"{self.ref} requires C++{self._min_cppstd}, "
                f"which {self.settings.compiler} {self.settings.compiler.version} does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BEEPING_USE_EXTERNAL_SPDLOG"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["BeepingCore"]
        self.cpp_info.set_property("cmake_file_name", "BeepingCore")
        self.cpp_info.set_property("cmake_target_name", "BeepingCore::BeepingCore")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m", "pthread"]
