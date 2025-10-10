from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

import os

required_conan_version = ">=2.0"


class DaggyConan(ConanFile):
    name = "daggy"
    license = "MIT"
    homepage = "https://daggy.gitbook.io/docs"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Data Aggregation Utility and C/C++ developer library for data streams catching"
    topics = ("streaming", "qt", "monitoring", "process", "stream-processing", "extensible", "serverless-framework", "aggregation", "ssh2", "crossplatform", "ssh-client")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_ssh2": [True, False],
        "with_yaml": [True, False],
        "with_console": [True, False],
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "with_ssh2": True,
        "with_yaml": True,
        "with_console": False,
        "shared": True,
        "fPIC": True
    }

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <5]")

    def validate(self):
        check_min_cppstd(self, "17")
            
    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("qt/[>=6.7 <7]", transitive_headers=True)
        self.requires("kainjow-mustache/4.1")

        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0")

        if self.options.with_ssh2:
            self.requires("libssh2/1.11.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        
        tc.cache_variables["SSH2_SUPPORT"] = self.options.with_ssh2
        tc.cache_variables["YAML_SUPPORT"] = self.options.with_yaml
        tc.cache_variables["CONSOLE"] = self.options.with_console
        tc.cache_variables["PACKAGE_DEPS"] = False
        tc.cache_variables["VERSION"] = "{}.0".format(self.version)
        tc.cache_variables["CONAN_BUILD"] = True
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["PORTABLE_BUILD"] = False

        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        if self.options.shared:
            tc.cache_variables["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            tc.cache_variables["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            tc.cache_variables["CMAKE_VISIBILITY_INLINES_HIDDEN"] = 1
        tc.generate() 

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["DaggyCore"]
        self.cpp_info.set_property("cmake_module_file_name", "DaggyCore")
        self.cpp_info.set_property("cmake_module_target_name", "daggy::DaggyCore")
        self.cpp_info.set_property("cmake_file_name", "DaggyCore")
        self.cpp_info.set_property("cmake_target_name", "daggy::DaggyCore")
        
        
