from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, copy, rm
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain

import os

required_conan_version = ">=2.0.0"


class PactFFIConan(ConanFile):
    name = "pact_ffi"
    description = "Pact/Rust FFI bindings"
    url = "https://gitlab.prod.entos.sky/immerse-ui/libs/Pact"
    homepage = "https://github.com/pact-foundation/pact-reference"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    topics = ("pact", "consumer-driven-contracts", "contract-testing", "mock-server")
    user = "sky"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    def source(self):
        get(self, "https://github.com/pact-foundation/pact-reference/archive/refs/tags/libpact_ffi-v0.4.21.tar.gz", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        # todo: release build
        # self.run(f"cargo build --target-dir={self.build_folder}", cwd=os.path.join(self.source_folder, "rust"))
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "rust", "pact_ffi"))
        cmake.build()

    def package(self):
        copy(self,
             "libpact_ffi*",
             os.path.join(self.build_folder),
             os.path.join(self.package_folder, "lib")
        )
        # TODO: locate generated headers
        copy(self, "pact*.h", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["pact_ffi"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
