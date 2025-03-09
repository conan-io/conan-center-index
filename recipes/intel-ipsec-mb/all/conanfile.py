from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4.0"


class PackageConan(ConanFile):
    name = "intel-ipsec-mb"
    description = "Intel(R) Multi-Buffer Crypto for IPSec"
    license = "BSD-3-Clause"
    homepage = "https://github.com/intel/intel-ipsec-mb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("intel", "ipsec", "crypto", "security")
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
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    @property
    def _cmake_target(self):
        return "libIPSec_MB" if is_msvc(self) else "IPSec_MB"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} does not support the O.S. {self.settings.os}.")
        if self.settings.arch not in ["x86", "x86_64"]:
            # Relies on x86 SIMD intrinsics.
            raise ConanInvalidConfiguration(f"{self.ref} does not support the architecture {self.settings.arch}.")

    def build_requirements(self):
        self.tool_requires("nasm/2.15.05")
        self.tool_requires("cmake/[>3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        # INFO: Conan 1.x does not find nasm package automatically due PATH priority.
        nasm_bin_folder = os.path.join(self.dependencies.direct_build["nasm"].package_folder, "bin").replace("\\", "/")
        nasm_path = os.path.join(nasm_bin_folder, "nasm").replace("\\", "/")
        env = Environment()
        env.define("AS", nasm_path)
        env.prepend("PATH", nasm_bin_folder)
        envvars = env.vars(self, scope="build")
        envvars.save_script("asm_configuration")

        tc = CMakeToolchain(self)
        # INFO: intel-ipsec-mb project forces shared by default.
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        # INFO: When running on Linux, uses /usr/bin/nasm in case no enforced
        if self.settings_build.os == "Linux":
            tc.cache_variables["CMAKE_ASM_NASM_COMPILER"] = nasm_path
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._cmake_target)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "intel-ipsec-mb.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "lib"), keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "man"))
        rmdir(self, os.path.join(self.package_folder, "intel-ipsec-mb"))

    def package_info(self):
        self.cpp_info.libs = [self._cmake_target]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
