from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.0"

class AdaConan(ConanFile):
    name = "ada"
    description = "WHATWG-compliant URL parser written in modern C++"
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ada-url/ada"
    topics = ("url", "parser", "WHATWG")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20 if Version(self.version) >= "3.0.0" else 17)

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "12.0.0" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires <charconv>, please use libc++ or upgrade compiler."
            )
        if Version(self.version) >= "3.0.0" and \
                ( \
                    # for std::ranges::any_of
                    (self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14.3")
                    # std::string_view is not constexpr in gcc < 12
                    or (self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "12") \
                ):
            raise ConanInvalidConfiguration(
                f"{self.ref} doesn't support {self.settings.compiler} {self.settings.compiler.version}"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["ADA_TESTING"] = False
        tc.variables["ADA_TOOLS"] = False
        if not is_msvc(self):
            tc.extra_cxxflags = ["-Wno-fatal-errors"]
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["ada"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
