# Conan Center recipe for intelliversex-cpp.
# Requires nakama-sdk in Conan Center (submit nakama-sdk first or document in PR).

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
import os


class IntelliversexCppConan(ConanFile):
    name = "intelliversex-cpp"
    version = "5.1.0"
    description = "IntelliVerseX C/C++ SDK — Auth, Backend (Nakama), Analytics, Social, Monetization for game development"
    license = "MIT"
    url = "https://github.com/Intelli-verse-X/Intelli-verse-X-Unity-SDK"
    homepage = "https://github.com/Intelli-verse-X/Intelli-verse-X-Unity-SDK"
    topics = ("game", "sdk", "nakama", "backend", "auth")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "nakama-sdk/2.9.0"

    def export_sources(self):
        copy(self, "conandata.yml", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src", build_folder="build")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        sdk_dir = os.path.join(self.source_folder, "SDKs", "cpp")
        cmake.configure(
            source_folder=sdk_dir,
            variables={
                "IVX_BUILD_TESTS": "OFF",
                "IVX_BUILD_EXAMPLES": "OFF",
                "IVX_BUILD_SHARED": "ON" if self.options.get_safe("shared", False) else "OFF",
            },
        )
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        license_src = os.path.join(self.source_folder, "LICENSE")
        if os.path.isfile(license_src):
            copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["intelliversex"]
        self.cpp_info.set_property("cmake_target_name", "intelliversex")
        self.cpp_info.names["cmake_find_package"] = "intelliversex"
        self.cpp_info.names["cmake_find_package_multi"] = "intelliversex"
