import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
)
from conan.tools.scm import Git

required_conan_version = ">=2.0.0"


class EdDonnaConan(ConanFile):
    name = "ed25519"
    description = "ed25519 is an Elliptic Curve Digital Signature Algorithm."
    url = "https://github.com/floodyberry/ed25519-donna.git"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openssl/*:shared": False,
    }

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")

    def export_sources(self):
        copy(
            self,
            "CMakeLists.txt",
            src=self.recipe_folder,
            dst=self.export_sources_folder,
        )
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        git = Git(self)
        git.fetch_commit(**self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ED25519_DONNA_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ed25519"]
        self.cpp_info.set_property("cmake_file_name", "ed25519")
        self.cpp_info.set_property("cmake_target_name", "ed25519::ed25519")
        self.cpp_info.requires = ["openssl::ssl"]
