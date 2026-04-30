from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd

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
        "shared": False,
        "fPIC": True
    }
    implements = ["auto_shared_fpic"]

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <5]")
        self.tool_requires("qt/<host_version>") # For Qt automoc

    def validate(self):
        check_min_cppstd(self, "17")
            
    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # INFO: Qt transitive libs is needed for QVariantMap in Sources.hpp
        self.requires("qt/[>=6.7 <7]", transitive_headers=True, transitive_libs=True)
        self.requires("kainjow-mustache/4.1")

        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0")

        if self.options.with_ssh2:
            self.requires("libssh2/1.11.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        tc = CMakeToolchain(self)
        qt_tools_rootdir = self.conf.get("user.qt:tools_directory", None)
        tc.cache_variables["CMAKE_AUTOMOC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "moc.exe" if self.settings_build.os == "Windows" else "moc")
        tc.cache_variables["SSH2_SUPPORT"] = self.options.with_ssh2
        tc.cache_variables["YAML_SUPPORT"] = self.options.with_yaml
        tc.cache_variables["CONSOLE"] = self.options.with_console
        tc.cache_variables["VERSION"] = "{}.0".format(self.version)
        tc.cache_variables["CONAN_BUILD"] = True
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["PORTABLE_BUILD"] = False
        tc.generate() 

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["DaggyCore"]
        self.cpp_info.set_property("cmake_file_name", "DaggyCore")
        self.cpp_info.set_property("cmake_target_name", "daggy::DaggyCore")
        
        
