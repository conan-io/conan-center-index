from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file
from conan.tools.gnu import PkgConfigDeps

import os


class KeychainConan(ConanFile):
    name = "keychain"
    homepage = "https://github.com/hrantzsch/keychain"
    description = "A cross-platform wrapper for the operating system's credential storage"
    topics = ("keychain", "security", "credentials", "password", "cpp11")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {'shared': [False, True], 'fPIC': [False, True]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libsecret/0.20.5")
            self.requires("glib/2.78.1")

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.tool_requires("pkgconf/2.0.3")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Ensure .dll is installed on Windows
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "TARGETS ${PROJECT_NAME}", "TARGETS ${PROJECT_NAME} RUNTIME DESTINATION bin")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        # Export all symbols by default to allow generating a shared library with msvc
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
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
