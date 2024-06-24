from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, copy, replace_in_file
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain

import os

required_conan_version = ">=2.0.0"


class PactFFIConan(ConanFile):
    name = "pact_ffi"
    version = "0.4.21"
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
        get(self, f"https://github.com/pact-foundation/pact-reference/archive/refs/tags/libpact_ffi-v{self.version}.tar.gz",
            strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CARGO_TARGET_DIR"] = os.path.join(self.build_folder, "rust", "target")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "rust", "pact_ffi", "CMakeLists.txt"),
                        'set(CARGO_TARGET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../target")',
                        'set(CARGO_TARGET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../target" CACHE STRING "")')
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "rust", "pact_ffi"))
        cmake.build()

        # Build the headers
        # Note: CMakeLists.txt only supports building the C header 'pact.h', via a "generate_header" custom target.
        #       For consistency, instead of cmake.build(target="generate_header"), we use the explicit commands to
        #       generate both C and C++ headers (as defined in pact_ffi/release-linux.sh)
        generated_headers_dir = os.path.join(self.source_folder, "rust", "pact_ffi", "include")
        pact_c_header = os.path.join(generated_headers_dir, "pact.h")
        self.run(f"rustup run nightly cbindgen --config cbindgen.toml --crate pact_ffi --output {pact_c_header}",
                 cwd=os.path.join(self.source_folder, "rust", "pact_ffi"))

        pact_cpp_header = os.path.join(generated_headers_dir, "pact-cpp.h")
        self.run(f"rustup run nightly cbindgen --config cbindgen-c++.toml --crate pact_ffi --output {pact_cpp_header}",
                 cwd=os.path.join(self.source_folder, "rust", "pact_ffi"))

    def package(self):
        copy(self,
             "libpact_ffi*",
             os.path.join(self.build_folder, "rust", "target", "release"),
             os.path.join(self.package_folder, "lib")
             )

        copy(self,
             "pact*.h",
             os.path.join(self.source_folder, "rust", "pact_ffi", "include"),
             os.path.join(self.package_folder, "include"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["pact_ffi"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
