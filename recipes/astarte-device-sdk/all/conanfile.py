from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.build import check_min_cppstd, check_min_compiler_version
import os

required_conan_version = ">=2.1"

class AstarteConan(ConanFile):
    name = "astarte-device-sdk"
    package_type = "library"
    languages = "C++"
    license = "Apache-2.0"
    author = "Simone Orru (simone.orru@secomind.com)"
    url = "https://github.com/astarte-platform/astarte-device-sdk-cpp"
    homepage = "https://docs.astarte-platform.org/"
    description = "Astarte device SDK package written in C++"
    topics = ("mqtt", "astarte", "iot")

    # Settings and options
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Build configuration
    build_policy = "missing"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("grpc/1.72.0")
        self.requires("protobuf/6.30.1", override = True)
        self.requires("spdlog/1.15.3", options={"use_std_fmt": "True"}, transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("protobuf/6.30.1")

    def validate(self):
        check_min_cppstd(self, 20)
        compiler_restrictions = [
            ("gcc", "13", "Requires C++20 std::format"),
            ("clang", "15", "Requires C++20 std::format"),
            ("apple-clang", "15", "Requires C++20 std::format"),
            ("msvc", "193", "Requires C++20 std::format") # Visual Studio 2022
        ]
        check_min_compiler_version(self, compiler_restrictions)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # exports_sources = "CMakeLists.txt", "cmake/AstarteMQTTTransport.cmake", "cmake/AstarteGRPCTransport.cmake", "cmake/Config.cmake.in", "cmake/pkg-config-template.pc.in", "src/*", "include/*", "private/*"

    def package_info(self):
        self.cpp_info.libs = ["astarte_device_sdk", "astarte_msghub_proto"]
        self.cpp_info.set_property("cmake_file_name", "astarte_device_sdk")
        self.cpp_info.set_property("cmake_target_name", "astarte_device_sdk::astarte_device_sdk")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASTARTE_USE_SYSTEM_SPDLOG"] = "ON"
        tc.variables["ASTARTE_USE_SYSTEM_GRPC"] = "ON"
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
