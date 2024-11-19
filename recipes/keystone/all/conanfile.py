from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    get,
    rmdir,
    export_conandata_patches,
    apply_conandata_patches,
)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class KeystoneConan(ConanFile):
    name = "keystone"
    description = (
        "Keystone assembler framework: Core (Arm, Arm64, Hexagon, "
        "Mips, PowerPC, Sparc, SystemZ & X86) + bindings."
    )
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.keystone-engine.org"
    topics = (
        "reverse-engineering",
        "disassembler",
        "security",
        "framework",
        "arm",
        "arm64",
        "x86",
        "sparc",
        "powerpc",
        "mips",
        "x86-64",
        "hexagon",
        "systemz",
    )
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_LIBS_ONLY"] = True
        tc.cache_variables["KEYSTONE_BUILD_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "COPYING",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "_dll" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"keystone{suffix}"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shell32", "ole32", "uuid"]
