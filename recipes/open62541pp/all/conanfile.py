import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
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
        "ipo": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ipo": False,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("open62541/1.4.6", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UAPP_INTERNAL_OPEN62541"] = False
        tc.variables["UAPP_BUILD_DOCUMENTATION"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.variables["open62541_ipo"] = self.options.ipo
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Otherwise fails with
        #   INTERFACE_LIBRARY targets may only have whitelisted properties.  The
        #   property "INTERPROCEDURAL_OPTIMIZATION" is not allowed.
        # Set this in CMakeToolchain instead
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "get_target_property(open62541_ipo open62541::open62541 INTERPROCEDURAL_OPTIMIZATION)", "")

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
