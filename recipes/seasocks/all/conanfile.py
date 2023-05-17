from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class SeasocksConan(ConanFile):
    name = "seasocks"
    description = "A tiny embeddable C++ HTTP and WebSocket server for Linux"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattgodbolt/seasocks"
    topics = ("embeddable", "webserver", "websockets")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "1.4.5" else 17

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "1.4.5":
            return {}
        else:
            return {
                "Visual Studio": "16",
                "msvc": "191",
                "gcc": "7",
                "clang": "7",
                "apple-clang": "10",
            }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support this os")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        # No warnings as errors
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "-Werror", "")
        replace_in_file(self, cmakelists, "-pedantic-errors", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DEFLATE_SUPPORT"] = self.options.with_zlib
        tc.variables["SEASOCKS_SHARED"] = self.options.shared
        tc.variables["SEASOCKS_EXAMPLE_APP"] = False
        tc.variables["UNITTESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Seasocks")
        self.cpp_info.set_property("cmake_target_name", "Seasocks::seasocks")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["libseasocks"].libs = ["seasocks"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libseasocks"].system_libs.extend(["pthread", "m"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Seasocks"
        self.cpp_info.names["cmake_find_package_multi"] = "Seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package"] = "seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package_multi"] = "seasocks"
        self.cpp_info.components["libseasocks"].set_property("cmake_target_name", "Seasocks::seasocks")
        if self.options.with_zlib:
            self.cpp_info.components["libseasocks"].requires = ["zlib::zlib"]
