import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get


class PolyxmlConan(ConanFile):
    name = "polyxml"
    description = "High-performance, polyglot native XML data-binding engine built in Rust"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nth-bailey/PolyXML"
    topics = ("xml", "deserializer", "serializer", "data-binding", "parser", "polyglot")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        # 1. Build the native polyxml-c library via cargo
        cargo_cmd = "cargo build --release -p polyxml-c"
        self.output.info(f"Building native Rust polyxml-c library: {cargo_cmd}")
        self.run(cargo_cmd)

        # 2. Build C++20 bindings via CMake
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "bindings", "cpp"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        # C++20 and C headers
        copy(
            self,
            "*.hpp",
            src=os.path.join(self.source_folder, "bindings", "cpp", "include"),
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "*.h",
            src=os.path.join(self.source_folder, "crates", "polyxml-c", "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

        # Compiled native libraries
        release_dir = os.path.join(self.source_folder, "target", "release")
        copy(self, "*.lib", src=release_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a", src=release_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", src=release_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=release_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=release_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["polyxml"]
        self.cpp_info.includedirs = ["include"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "userenv", "ntdll"])
