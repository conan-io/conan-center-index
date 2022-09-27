from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "fmtlog"
    description = "fmtlog is a performant fmtlib-style logging library with latency in nanoseconds."
    license = "MIT license"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/MengRao/fmtlog"
    topics = ("logging", "low-latency", "topic3") # no "conan" and project name in topics
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/9.1.0")

    def package_id(self):
        if self.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        be = VirtualBuildEnv(self)
        be.generate(scope="build")

    def build(self):
        if self.options.header_only:
            return
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self, pattern="fmtlog*.h", dst=os.path.join(self.package_folder, "include", "fmtlog"), src=self.source_folder)
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines.append("FMTLOG_HEADER_ONLY")
        else:
            self.cpp_info.libs = ["fmtlog-shared" if self.options.shared else "fmtlog-static"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
