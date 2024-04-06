from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class MBitsDiagsConan(ConanFile):
    name = "mbits-diags"
    description = "Diagnostic library with source positions, ranges and hints."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mbits-libs/diags"
    topics = ("diagnostics", "cli", "logging", "errors")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "11.0.3",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.2.1")
        self.requires("mbits-semver/0.1.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False
            )
            if (
                minimum_version
                and Version(self.settings.compiler.version) < minimum_version
            ):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DIAGS_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["diags"]

        self.cpp_info.set_property("cmake_file_name", "mbits-diags")
        self.cpp_info.set_property("cmake_target_name", "mbits::diags")

        self.cpp_info.filenames["cmake_find_package"] = "mbits-diags"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mbits-diags"
        self.cpp_info.names["cmake_find_package"] = "mbits"
        self.cpp_info.names["cmake_find_package_multi"] = "mbits"
        self.cpp_info.components["diags"].set_property(
            "cmake_target_name", "mbits::diags"
        )
        self.cpp_info.components["diags"].libs = ["diags"]
        self.cpp_info.components["diags"].requires = [
            "fmt::fmt",
            "mbits-semver::semver",
        ]
