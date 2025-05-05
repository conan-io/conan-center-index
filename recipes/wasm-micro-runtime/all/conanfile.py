from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class WasmMicroRuntimeConan(ConanFile):
    name = "wasm-micro-runtime"
    description = "WebAssembly Micro Runtime (WAMR)"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bytecodealliance.github.io/wamr.dev/"
    topics = ("wasm", "embedded", "webassembly", "runtime")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_interp": [False, "fast", "classic"],
        "with_aot": [True, False],
        "with_jit": [True, False],
        "with_fast_jit": [True, False],
        "libc": ["builtin", "wasi", "uvwasi"],
        "with_multi_module": [True, False],
        "with_mini_loader": [True, False],
        "with_pthread": [True, False],
        "with_wasi_threads": [True, False],
        "with_tail_call": [True, False],
        "with_simd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_interp": "fast",
        "with_aot": True,
        "with_jit": False,
        "with_fast_jit": False,
        "libc": "builtin",
        "with_multi_module": False,
        "with_mini_loader": False,
        "with_pthread": False,
        "with_wasi_threads": False,
        "with_tail_call": False,
        "with_simd": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # When with_fast_jit is True, C++ is required.
        if not self.options.with_fast_jit:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # When with_fast_jit is True, C++ is required.
        if not self.options.with_fast_jit:
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, 11)
        if not self.options.with_interp and not self.options.with_aot:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_interp and with_aot at least one.")
        if self.options.with_jit:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_jit(yet).")
        if self.options.with_multi_module and self.options.with_mini_loader:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support both with_multi_module and with_mini_loader.")
        if self.options.libc == "wasi" and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support libc=wasi on Windows.")
        if self.options.libc == "uvwasi":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support libc=uvwasi(yet).")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def is_enabled(value):
            return 1 if value else 0

        tc = CMakeToolchain(self)
        # FIXME: it should use assembler code instead of C++ on MSVC
        if is_msvc(self):
            tc.variables["WAMR_BUILD_INVOKE_NATIVE_GENERAL"] = 1

        # interpreters
        tc.variables["WAMR_BUILD_INTERP"] = is_enabled(self.options.with_interp)
        if self.options.with_interp:
            tc.variables["WAMR_BUILD_FAST_INTERP"] = is_enabled(self.options.with_interp == "fast")
        # AOT and JITs
        tc.variables["WAMR_BUILD_AOT"] = is_enabled(self.options.with_aot)
        tc.variables["WAMR_BUILD_JIT"] = is_enabled(self.options.with_jit)
        tc.variables["WAMR_BUILD_FAST_JIT"] = is_enabled(self.options.with_fast_jit)
        # LIBC
        tc.variables["WAMR_BUILD_LIBC_BUILTIN"] = is_enabled(self.options.libc == "builtin")
        tc.variables["WAMR_BUILD_LIBC_WASI"] = is_enabled(self.options.libc == "wasi")
        tc.variables["WAMR_BUILD_LIBC_UVWASI"] = is_enabled(self.options.libc == "uvwasi")
        # others
        tc.variables["WAMR_BUILD_MULTI_MODULE"] = is_enabled(self.options.with_multi_module)
        tc.variables["WAMR_BUILD_MINI_LOADER"] = is_enabled(self.options.with_mini_loader)
        tc.variables["WAMR_BUILD_LIB_PTHREAD"] = is_enabled(self.options.with_pthread)
        tc.variables["WAMR_BUILD_LIB_WASI_THREADS"] = is_enabled(self.options.with_wasi_threads)
        tc.variables["WAMR_BUILD_TAIL_CALL"] = is_enabled(self.options.with_tail_call)
        tc.variables["WAMR_BUILD_SIMD"] = is_enabled(self.options.with_simd)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["iwasm" if self.options.shared else "vmlib"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("COMPILING_WASM_RUNTIME_API=0")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
