from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"

class Re2Conan(ConanFile):
    name = "re2"
    description = "Fast, safe, thread-friendly regular expression library"
    topics = ("regex",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/re2"
    license = "BSD-3-Clause"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_icu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_icu": False,
    }

    @property
    def _min_cppstd(self):
        return 14 if Version(self.version) >= "20230601" else 11

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "6",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "20230201":
            del self.options.with_icu

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_icu"):
            self.requires("icu/73.2")
        if Version(self.version) >= "20230601":
            self.requires("abseil/20230125.3", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RE2_BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "re2")
        self.cpp_info.set_property("cmake_target_name", "re2::re2")
        self.cpp_info.set_property("pkg_config_name", "re2")
        self.cpp_info.libs = ["re2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
