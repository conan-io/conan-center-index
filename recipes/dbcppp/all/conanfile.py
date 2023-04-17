from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class DBCpppConan(ConanFile):
    name = "dbcppp"
    description = ".dbc library for C/C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xR3b0rn/dbcppp"
    topics = ("can", "dbc", "network")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_tools": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_tools": False,
    }

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "12",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tools:
            self.requires("cxxopts/3.0.0")
        self.requires("boost/1.80.0")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["build_tests"] = False
        tc.variables["build_examples"] = False
        tc.variables["build_tools"] = self.options.with_tools
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        rm(self, "KCD2Network.cpp", self.source_folder, recursive=True) # Cannot support KCD because of weird dll issues
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["libdbcppp"]
        if self.info.option.with_tools:
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
