import os
from conan import ConanFile, tools
from conans import CMake


class CapstoneConan(ConanFile):
    name = "capstone"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.capstone-engine.org"
    description = "Capstone disassembly/disassembler framework: Core (Arm, Arm64, BPF, EVM, M68K, M680X, MOS65xx, Mips, PPC, RISCV, Sparc, SystemZ, TMS320C64x, Web Assembly, X86, X86_64, XCore) + bindings."
    topics = ("conan", 'reverse-engineering', 'disassembler', 'security', 'framework', 'arm', 'arm64', 'x86', 'sparc', 'powerpc', 'mips', 'x86-64', 'ethereum', 'systemz', 'webassembly', 'm68k', 'm0s65xx', 'm680x', 'tms320c64x', 'bpf', 'riscv')
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_default_alloc": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_default_alloc": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None
    _archs = ['arm', 'm68k', 'mips', 'ppc', 'sparc', 'sysz', 'xcore', 'x86', 'tms320c64x', 'm680x', 'evm']
    options.update({a: [True, False] for a in _archs})
    default_options.update({a: True for a in _archs})

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions['CAPSTONE_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['CAPSTONE_BUILD_SHARED'] = self.options.shared
        cmake.definitions['CAPSTONE_BUILD_TESTS'] = False
        cmake.definitions['CAPSTONE_BUILD_CSTOOL'] = False
        cmake.definitions['CAPSTONE_ARCHITECUTRE_DEFAULT'] = False
        cmake.definitions['CAPSTONE_USE_SYS_DYN_MEM'] = self.options.use_default_alloc
        for a in self._archs:
            cmake.definitions['CAPSTONE_%s_SUPPORT' % a.upper()] = self.options.get_safe(a)
        runtime = self.settings.get_safe("compiler.runtime")
        if runtime:
            cmake.definitions['CAPSTONE_BUILD_STATIC_RUNTIME'] = 'MT' in runtime
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_LLVM.txt", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # FIXME : add components, if needed

    def package_info(self):
        if self.options.shared:
            self.cpp_info.defines.append('CAPSTONE_SHARED')
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.libs = ["capstone_dll"]
        else:
            self.cpp_info.libs = ["capstone"]
