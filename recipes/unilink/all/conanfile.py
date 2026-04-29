from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("boost/[>=1.88.0]", transitive_headers=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["UNILINK_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["UNILINK_ENABLE_INSTALL"] = True
        tc.cache_variables["UNILINK_BUILD_EXAMPLES"] = False
        tc.cache_variables["UNILINK_BUILD_TESTS"] = False
        tc.cache_variables["UNILINK_BUILD_DOCS"] = False
        tc.cache_variables["UNILINK_ENABLE_PKGCONFIG"] = False
        tc.cache_variables["UNILINK_ENABLE_CONFIG"] = self.options.enable_config
        tc.cache_variables["UNILINK_ENABLE_MEMORY_TRACKING"] = self.options.enable_memory_tracking
        tc.generate()

        deps = CMakeDeps(self)
        if Version(self.dependencies["boost"].ref.version) >= "1.89.0":
            deps.set_property("boost::headers", "cmake_target_aliases", ["Boost::system"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy license files
        copy(
            self,
            "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        if os.path.isfile(os.path.join(self.source_folder, "NOTICE")):
            copy(
                self,
                "NOTICE",
                src=self.source_folder,
                dst=os.path.join(self.package_folder, "licenses"),
            )

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
        self.cpp_info.requires = ["boost::headers"]
