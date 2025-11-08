from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class UnilinkConan(ConanFile):
    name = "unilink"
    description = "Unified async communication library for TCP and Serial communication"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jwsung91/unilink"
    topics = ("async", "communication", "tcp", "serial", "networking", "c++17")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_config": [True, False],
        "enable_memory_tracking": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_config": True,
        "enable_memory_tracking": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least GCC 7")

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least Clang 5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("boost/[>=1.83.0 <2]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UNILINK_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["UNILINK_BUILD_STATIC"] = not bool(self.options.shared)
        tc.variables["UNILINK_ENABLE_INSTALL"] = True
        tc.variables["UNILINK_BUILD_EXAMPLES"] = False
        tc.variables["UNILINK_BUILD_TESTS"] = False
        tc.variables["UNILINK_BUILD_DOCS"] = False
        tc.variables["UNILINK_ENABLE_PKGCONFIG"] = False
        tc.variables["UNILINK_ENABLE_CONFIG"] = bool(self.options.enable_config)
        tc.variables["UNILINK_ENABLE_MEMORY_TRACKING"] = bool(self.options.enable_memory_tracking)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy license files
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Set target name
        self.cpp_info.set_property("cmake_target_name", "unilink::unilink")
        self.cpp_info.set_property("cmake_file_name", "unilink")
        self.cpp_info.set_property("pkg_config_name", "unilink")
        self.cpp_info.libs = ["unilink"]

        # Set compile definitions
        if self.options.enable_config:
            self.cpp_info.defines.append("UNILINK_ENABLE_CONFIG=1")
        if self.options.enable_memory_tracking:
            self.cpp_info.defines.append("UNILINK_ENABLE_MEMORY_TRACKING=1")

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")

        # Boost dependency
        self.cpp_info.requires = ["boost::boost", "boost::system"]
