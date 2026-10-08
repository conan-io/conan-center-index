import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc

required_conan_version = ">=2.1"


class Open62541ppConan(ConanFile):
    name = "open62541pp"
    description = "open62541++ is a C++ wrapper built on top of the amazing open62541 OPC UA (OPC Unified Architecture) library"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open62541pp/open62541pp"
    topics = ("opcua", "open62541")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("open62541/[~1.4.14]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UAPP_INTERNAL_OPEN62541"] = False
        tc.variables["UAPP_BUILD_DOCUMENTATION"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

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
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["open62541pp"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
