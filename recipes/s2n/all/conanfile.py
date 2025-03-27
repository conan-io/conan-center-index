from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.4"


class S2nConan(ConanFile):
    name = "s2n"
    description = "An implementation of the TLS/SSL protocols"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/s2n-tls"
    topics = ("aws", "amazon", "cloud", )
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
    languages = "C"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Not supported (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["UNSAFE_TREAT_WARNINGS_AS_ERRORS"] = False
        tc.variables["SEARCH_LIBCRYPTO"] = False # see CMakeLists wrapper
        # When adding new version, check if they updated their minimum CMake version and make this conditional
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "s2n"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "s2n")
        self.cpp_info.set_property("cmake_target_name", "AWS::s2n")
        self.cpp_info.libs = ["s2n"]
        self.cpp_info.requires = ["openssl::crypto"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m", "pthread"]
