from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class JsonnetConan(ConanFile):
    name = "jsonnet"
    description = "Jsonnet - The data templating language"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/jsonnet"
    topics = ("config", "json", "functional", "configuration")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

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
        self.requires("nlohmann_json/3.11.2")
        if Version(self.version) >= "0.18.0":
            self.requires("rapidyaml/0.5.0")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration(f"{self.ref} does not support cross building")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.options.shared and is_msvc(self) and "d" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration(f"shared {self.ref} is not supported with MTd/MDd runtime")

        # This is a workround.
        # If jsonnet is shared, rapidyaml must be built as shared,
        # or the c4core functions that rapidyaml depends on will not be able to be found.
        # This seems to be a issue of rapidyaml.
        # https://github.com/conan-io/conan-center-index/pull/9786#discussion_r829887879
        if self.options.shared and Version(self.version) >= "0.18.0" and self.dependencies["rapidyaml"].options.shared == False:
            raise ConanInvalidConfiguration(f"shared {self.ref} requires rapidyaml to be built as shared")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_SHARED_BINARIES"] = False
        tc.variables["BUILD_JSONNET"] = False
        tc.variables["BUILD_JSONNETFMT"] = False
        tc.variables["USE_SYSTEM_JSON"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libjsonnet"].libs = ["jsonnet"]
        self.cpp_info.components["libjsonnet"].requires = ["nlohmann_json::nlohmann_json"]
        if Version(self.version) >= "0.18.0":
            self.cpp_info.components["libjsonnet"].requires.append("rapidyaml::rapidyaml")

        if stdcpp_library(self):
            self.cpp_info.components["libjsonnet"].system_libs.append(stdcpp_library(self))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libjsonnet"].system_libs.append("m")

        self.cpp_info.components["libjsonnetpp"].libs = ["jsonnet++"]
        self.cpp_info.components["libjsonnetpp"].requires = ["libjsonnet"]
