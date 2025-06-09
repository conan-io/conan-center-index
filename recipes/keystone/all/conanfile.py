from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.build import check_max_cppstd
import os

required_conan_version = ">=2.1"


class KeystoneConan(ConanFile):
    name = "keystone"
    description = (
        "Keystone assembler framework: Core (Arm, Arm64, Hexagon, "
        "Mips, PowerPC, Sparc, SystemZ & X86) + bindings."
    )
    license = ( "GPL-2.0-only", "DocumentRef-EXCEPTIONS-CLIENT:LicenseRef-FOSS-License-Exception" )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.keystone-engine.org"
    topics = (
        "security",
        "arm",
        "framework",
        "mips",
        "x86-64",
        "reverse-engineering",
        "assembler",
        "x86",
        "hexagon",
        "arm64",
        "sparc",
        "powerpc",
        "systemz"
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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def validate(self):
        # INFO: include/llvm/ADT/STLExtras.h:54:34: error: no template named 'binary_function' in namespace 'std'
        # The std::binary_function was removed in C++17
        check_max_cppstd(self, 14)

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
        copy(
            self,
            "EXCEPTIONS-CLIENT",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["keystone"]
        if is_msvc(self) and self.options.shared:
            self.cpp_info.bindirs = ["lib"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shell32", "ole32", "uuid"]
