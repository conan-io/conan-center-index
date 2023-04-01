from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get
from conan.tools.gnu import PkgConfigDeps

import os


class KeychainConan(ConanFile):
    name = "keychain"
    homepage = "https://github.com/hrantzsch/keychain"
    description = "A cross-platform wrapper for the operating system's credential storage"
    topics = ("keychain", "security", "credentials", "password", "cpp11")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {'shared': [False, True], 'fPIC': [False, True]}
    default_options = {"shared": False, "fPIC": True}

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libsecret/0.20.4")

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("pkgconf/1.7.3")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()
        pc = PkgConfigDeps(self)
        pc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ['Security', 'CoreFoundation']
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ['crypt32']
