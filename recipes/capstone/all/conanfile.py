from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"


class CapstoneConan(ConanFile):
    name = "capstone"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.capstone-engine.org"
    description = (
        "Capstone disassembly/disassembler framework: Core (Arm, Arm64, BPF, "
        "EVM, M68K, M680X, MOS65xx, Mips, PPC, RISCV, Sparc, SystemZ, "
        "TMS320C64x, Web Assembly, X86, X86_64, XCore) + bindings."
    )
    topics = (
        "reverse-engineering", "disassembler", "security", "framework", "arm", "arm64",
        "x86", "sparc", "powerpc", "mips", "x86-64", "ethereum", "systemz",
        "webassembly", "m68k", "m0s65xx", "m680x", "tms320c64x", "bpf", "riscv",
    )

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_default_alloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_default_alloc": True,
    }

    _archs = ["arm", "m68k", "mips", "ppc", "sparc", "sysz", "xcore", "x86", "tms320c64x", "m680x", "evm"]
    options.update({a: [True, False] for a in _archs})
    default_options.update({a: True for a in _archs})

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CAPSTONE_BUILD_STATIC"] = not self.options.shared
        tc.variables["CAPSTONE_BUILD_SHARED"] = self.options.shared
        tc.variables["CAPSTONE_BUILD_TESTS"] = False
        tc.variables["CAPSTONE_BUILD_CSTOOL"] = False
        tc.variables["CAPSTONE_ARCHITECUTRE_DEFAULT"] = False
        tc.variables["CAPSTONE_USE_SYS_DYN_MEM"] = self.options.use_default_alloc
        for a in self._archs:
            tc.variables[f"CAPSTONE_{a.upper()}_SUPPORT"] = self.options.get_safe(a)
        tc.variables["CAPSTONE_BUILD_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        suffix = "_dll" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"capstone{suffix}"]
        if self.options.shared:
            self.cpp_info.defines.append("CAPSTONE_SHARED")
