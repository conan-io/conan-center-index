import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class WasmtimeConan(ConanFile):
    name = "wasmtime"
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bytecodealliance/wasmtime"
    topics = ("webassembly", "wasm", "wasi")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "apple-clang": "9.4",
            "clang": "3.3",
            "gcc": "5.1",
        }

    @property
    def _sources_os_key(self):
        if is_msvc(self):
            return "Windows"
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            return "MinGW"
        return str(self.settings.os)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def package_id(self):
        del self.info.settings.compiler.version
        if self.info.settings.compiler == "clang":
            self.info.settings.compiler = "gcc"

    def validate(self):
        try:
            self.conan_data["sources"][self.version][self._sources_os_key][str(self.settings.arch)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os are not available")

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build(self):
        # This is packaging binaries so the download needs to be in build
        get(self, **self.conan_data["sources"][self.version][self._sources_os_key][str(self.settings.arch)],
            destination=self.build_folder, strip_root=True)

    def package(self):
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.build_folder, "include"))

        srclibdir = os.path.join(self.build_folder, "lib")
        dstlibdir = os.path.join(self.package_folder, "lib")
        dstbindir = os.path.join(self.package_folder, "bin")
        if self.options.shared:
            copy(self, "wasmtime.dll.lib", dst=dstlibdir, src=srclibdir, keep_path=False)
            copy(self, "wasmtime.dll", dst=dstbindir, src=srclibdir, keep_path=False)
            copy(self, "libwasmtime.dll.a", dst=dstlibdir, src=srclibdir, keep_path=False)
            copy(self, "libwasmtime.so*", dst=dstlibdir, src=srclibdir, keep_path=False)
            copy(self, "libwasmtime.dylib",  dst=dstlibdir, src=srclibdir, keep_path=False)
        else:
            copy(self, "wasmtime.lib", dst=dstlibdir, src=srclibdir, keep_path=False)
            copy(self, "libwasmtime.a", dst=dstlibdir, src=srclibdir, keep_path=False)

        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.build_folder)

    def package_info(self):
        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.libs = ["wasmtime.dll"]
            else:
                self.cpp_info.libs = ["wasmtime"]
        else:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["WASM_API_EXTERN=", "WASI_API_EXTERN="]
            self.cpp_info.libs = ["wasmtime"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "bcrypt", "advapi32", "userenv", "ntdll", "shell32", "ole32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m", "rt"]
