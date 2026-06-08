from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"

class IdnaConan(ConanFile):
    name = "idna"
    description = "C++ library implementing the to_ascii and to_unicode functions from the Unicode Technical Standard."
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ada-url/idna/"
    topics = ("unicode", "icu")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)
        # apple-clang <= 14 doesn't support C++20 std::any_of which idna uses
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) <= "14":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support apple-clang <= 14")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["ADA_IDNA_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE-*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ada-idna"]
        self.cpp_info.set_property("cmake_file_name", "ada-idna")
        self.cpp_info.set_property("cmake_target_name", "ada-idna")
