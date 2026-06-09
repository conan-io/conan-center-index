from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=2.1"


class NekoEventConan(ConanFile):
    name = "neko-event"
    license = "MIT OR Apache-2.0"
    homepage = "https://github.com/moehoshio/NekoEvent"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A modern easy to use type-safe and high-performance event handling system for C++"
    topics = ("c++20", "header-only", "event", "neko", "event-dispatcher", "event-bus", "event-system", "pub-sub", "observer-pattern")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "header-library"
    implements = "auto_header_only"

    def requirements(self):
        self.requires("neko-schema/1.1.5", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NEKO_EVENT_BUILD_TESTS"] = False
        tc.cache_variables["NEKO_EVENT_ENABLE_MODULE"] = False
        tc.cache_variables["NEKO_EVENT_AUTO_FETCH_DEPS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "NekoEvent")
        self.cpp_info.set_property("cmake_target_name", "Neko::Event")
