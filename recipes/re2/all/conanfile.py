from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"

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

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_icu"):
            self.requires("icu/73.2")
        if Version(self.version) >= "20230601":
            self.requires("abseil/20240116.1", transitive_headers=True)

    def validate(self):
        if Version(self.version) >= "20250805":
            min_cppstd = 17
        elif Version(self.version) >= "20230601":
            min_cppstd = 14
        else:
            min_cppstd = 11
        check_min_cppstd(self, min_cppstd)

        if "abseil" in self.dependencies.host:
            abseil_cppstd = self.dependencies.host['abseil'].info.settings.compiler.cppstd
            if abseil_cppstd != self.settings.compiler.cppstd:
                raise ConanInvalidConfiguration(f"re2 and abseil must be built with the same compiler.cppstd setting")

    def build_requirements(self):
        if Version(self.version) >= "20250805":
            self.tool_requires("cmake/[>=3.22]")

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
