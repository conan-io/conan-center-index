from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class H3Conan(ConanFile):
    name = "h3"
    description = "Hexagonal hierarchical geospatial indexing system."
    license = "Apache-2.0"
    topics = ("hierarchical", "geospatial", "indexing")
    homepage = "https://github.com/uber/h3"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_filters": [True, False],
        "h3_prefix": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_filters": True,
        "h3_prefix": "",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if Version(self.version) >= "4.1.0":
            self.tool_requires("cmake/[>=3.20 <4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["H3_PREFIX"] = self.options.h3_prefix
        tc.variables["ENABLE_COVERAGE"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["BUILD_FILTERS"] = self.options.build_filters
        tc.variables["BUILD_GENERATORS"] = False
        tc.variables["WARNINGS_AS_ERRORS"] = False
        tc.variables["ENABLE_FORMAT"] = False
        tc.variables["ENABLE_LINTING"] = False
        tc.variables["ENABLE_DOCS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "h3")
        self.cpp_info.set_property("cmake_target_name", "h3::h3")
        self.cpp_info.libs = ["h3"]
        self.cpp_info.defines.append(f"H3_PREFIX={self.options.h3_prefix}")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.options.build_filters:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
