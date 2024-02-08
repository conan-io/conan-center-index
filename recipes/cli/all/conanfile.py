from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

class CLIConan(ConanFile):
    name = "cli"
    description = "A library for interactive command line interfaces in modern C++"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/daniele77/cli"
    topics = "cli-interface", "cpp14", "no-dependencies", "header-only"
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"with_asio": [None, "boost", "standalone"]}
    default_options = {"with_asio": None}
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "14",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_asio == "boost":
            self.requires("boost/1.84.0", transitive_headers=True, transitive_libs=True)
        elif self.options.with_asio == "standalone":
            self.requires("asio/1.29.0", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        # INFO: The options does not affect the package content, it's always the same.
        # On the other hand, dependencies are included or not depending on the options.
        # The CLI has no define or other way to include headers, is always the same,
        # the user should know what should be included.
        self.info.settings.clear()
        self.info.options.clear()

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
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["CLI_UseBoostAsio"] = self.options.with_asio == "boost"
        tc.variables["CLI_UseStandaloneAsio"] = self.options.with_asio == "standalone"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
