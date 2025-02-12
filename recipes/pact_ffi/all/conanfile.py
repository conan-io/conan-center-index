from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import get, copy, replace_in_file, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout

from pathlib import Path
import os


required_conan_version = ">=2.0.0"


class PactFFIConan(ConanFile):
    name = "pact_ffi"
    description = "Pact/Rust FFI bindings"
    url = "https://gitlab.prod.entos.sky/entos-xe/libs/Pact"
    homepage = "https://github.com/pact-foundation/pact-reference"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    topics = ("pact", "consumer-driven-contracts", "contract-testing", "mock-server")
    user = "sky"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # don't need these settings for a library with a C API
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("bzip2/1.0.8")

    def validate(self):
        if self.settings.build_type in ["RelWithDebInfo", "MinSizeRel"]:
            raise ConanInvalidConfiguration("build_type must be Release or Debug")
        if self.conf.get("tools.cmake.cmaketoolchain:generator") == "Ninja":
            raise ConanInvalidConfiguration("The Ninja generator is not supported. Define "
                                            "'pact_ffi/*:tools.cmake.cmaketoolchain:generator=!' in a profile to unset it")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _rust_target_triple(self):
        arch_lookup = {
            "armv8": "aarch64"
        }
        vendor_lookup = {
            "Macos": "apple"
        }
        os_lookup = {
            "Macos": "darwin"
        }
        return (f"{arch_lookup.get(str(self.settings.arch), 'x86_64')}-"
                f"{vendor_lookup.get(str(self.settings.os), 'unknown')}-"
                f"{os_lookup.get(str(self.settings.os), 'linux')}")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables.update({
            "CARGO_TARGET_DIR": str(Path(self.build_folder) / "rust" / "target"),
            "PACT_FFI_BUILD_DOCS": False
        })
        if cross_building(self):
            tc.cache_variables["CARGO_TARGET_TRIPLE"] = self._rust_target_triple()
        tc.generate()

        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "rust", "pact_ffi"))
        cmake.build()
        cmake.build(target="generate_headers")

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Pact will install shared libraries itself, but if we want static libs we have to do it manually
        package_folder = Path(self.package_folder)
        lib_folder = package_folder / "lib"
        if not self.options.shared:
            build_type = Path(str(self.settings.build_type).lower())
            subfolder = build_type if not cross_building(self) else self._rust_target_triple() / build_type
            target_folder = Path(self.build_folder) / "rust" / "target" / subfolder
            copy(self, pattern="*.a", src=target_folder, dst=lib_folder, excludes=["build/*", "deps/*"])
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
