from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import get, copy, replace_in_file, rmdir, rm
from conan.tools.layout import basic_layout

from pathlib import Path
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.build_type in ["RelWithDebInfo", "MinSizeRel"]:
            raise ConanInvalidConfiguration("build_type must be Release or Debug")
        if self.conf.get("tools.cmake.cmaketoolchain:generator") == "Ninja":
            raise ConanInvalidConfiguration("The Ninja generator is not supported. Define "
                                            "'pact_ffi/*:tools.cmake.cmaketoolchain:generator=!' in a profile to unset it")

    def layout(self):
        basic_layout(self, src_folder="src")

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
                        'set(CARGO_TARGET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../target" CACHE STRING "")', strict=False)
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
        cmake = CMake(self)
        cmake.install()

        # Pact will install shared libraries itself, but if we want static libs we have to do it manually
        package_folder = Path(self.package_folder)
        lib_folder = package_folder / "lib"
        if not self.options.shared:
            target_folder = Path(self.build_folder) / "rust" / "target" / str(self.settings.build_type).lower()
            copy(self, pattern="*.a", src=target_folder, dst=lib_folder)
            rm(self, pattern="*.so", folder=lib_folder)
            rm(self, pattern="*.dylib", folder=lib_folder)
        else:
            fix_apple_shared_install_name(self)

        # Don't include package generated cmake files as conan will generate its own
        rmdir(self, lib_folder / "cmake")
        copy(self, pattern="LICENSE", dst=package_folder / "licenses", src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["pact_ffi"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Security", "IOKit", "CoreFoundation", "SystemConfiguration"])
