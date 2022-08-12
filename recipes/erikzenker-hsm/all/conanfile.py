from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.47.0"


class HsmConan(ConanFile):
    name = "erikzenker-hsm"
    license = "MIT"
    homepage = "https://github.com/erikzenker/hsm.git"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "The hana state machine (hsm) is a finite state machine library based "
        "on the boost hana meta programming library. It follows the principles "
        "of the boost msm and boost sml libraries, but tries to reduce own "
        "complex meta programming code to a minimum."
    )
    topics = ("state-machine", "template-meta-programming")

    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        # FIXME: should use self.info.settings instead of self.settings for conan v2
        # https://github.com/erikzenker/hsm#dependencies
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration("clang 8+ is required")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "8":
            raise ConanInvalidConfiguration("GCC 8+ is required")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hsm"
        self.cpp_info.names["cmake_find_package_multi"] = "hsm"
        self.cpp_info.set_property("cmake_file_name", "hsm")
        self.cpp_info.set_property("cmake_target_name", "hsm::hsm")
