from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir, apply_conandata_patches, copy, export_conandata_patches
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SevenBitConfConan(ConanFile):
    name = "7bitconf"
    homepage = "https://github.com/7bitCoder/7bitConf"
    description = "7bitConf is a simple C++17 centralized configuration provider library."
    topics = ("cpp17", "configuration", "provider", "configuration-files")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17
    
    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared") or self.options.header_only:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            self.options.rm_safe("shared")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("taocpp-json/1.0.0-beta.14", transitive_headers=True)

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        compiler = self.settings.compiler
        compiler_name = str(compiler)

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(compiler_name, False)
        if minimum_version and Version(compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"Requires compiler {compiler_name} minimum version: {minimum_version} with C++17 support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["_7BIT_CONF_BUILD_EXAMPLES"] = False
            tc.variables["_7BIT_CONF_BUILD_TESTS"] = False
            tc.variables["_7BIT_CONF_BUILD_SINGLE_HEADER"] = False
            tc.variables["_7BIT_CONF_INSTALL"] = True
            tc.variables["_7BIT_CONF_LIBRARY_TYPE"] = self.getSevenBitConfLibraryType()
            tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def getSevenBitConfLibraryType(self):
        if self.options.header_only:
            return "HeaderOnly"
        if self.options.shared:
            return "Shared"
        return "Static"

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        if self.options.header_only:
            copy(
                self,
                src=os.path.join(self.source_folder, "Include"),
                pattern="*.hpp",
                dst=os.path.join(self.package_folder, "include"),
            )
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "7bitConf")
        self.cpp_info.set_property("cmake_target_name", "7bitConf::7bitConf")
        self.cpp_info.requires = ["taocpp-json::taocpp-json"]

        if self.options.header_only:
            self.cpp_info.libs = []
            self.cpp_info.bindirs = []
        else:
            suffix = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["7bitConf" + suffix]

            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
