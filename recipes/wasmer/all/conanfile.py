from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class WasmerConan(ConanFile):
    name = "wasmer"
    description = "The leading WebAssembly Runtime supporting WASI and Emscripten"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wasmerio/wasmer/"
    topics = ("webassembly", "wasm", "wasi", "emscripten")
    settings = "os", "arch", "compiler"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    @property
    def _compiler_alias(self):
        return {
            "Visual Studio": "Visual Studio",
            "msvc": "Visual Studio",
        }.get(str(self.settings.compiler), "gcc")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if is_msvc(self) and self.options.shared:
            del self.settings.compiler.runtime

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        try:
            self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of version/os/arch/compiler are not available")

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared Windows build of wasmer are non-working atm (no import libraries are available)")

        if self.settings.os == "Linux" and self.options.shared and "2.3.0" <= Version(self.version):
            raise ConanInvalidConfiguration("Shared Linux build of wasmer are not working. It requires glibc >= 2.25")

        if is_msvc(self) and not self.options.shared and self.settings.compiler.runtime != "MT":
            raise ConanInvalidConfiguration("wasmer is only available with compiler.runtime=MT")

    def package_id(self):
        del self.info.settings.compiler.version
        self.info.settings.compiler = self._compiler_alias

    def source(self):
        get(
            self, 
            **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias], destination=self.source_folder
        )

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        self.copy("*.h", src=os.path.join(self.source_folder, "include"), dst="include", keep_path=False)

        srclibdir = os.path.join(self.source_folder, "lib")
        dstlibdir = os.path.join(self.package_folder, "lib")
        dstbindir = os.path.join(self.package_folder, "bin")
        if self.options.shared:
            self.copy("wasmer.dll.lib", src=srclibdir, dst=dstlibdir, keep_path=False)  # FIXME: not available (yet)
            self.copy("wasmer.dll", src=srclibdir, dst=dstbindir, keep_path=False)
            self.copy("libwasmer.so*", src=srclibdir, dst=dstlibdir, keep_path=False)
            self.copy("libwasmer.dylib", src=srclibdir,  dst=dstlibdir, keep_path=False)
        else:
            self.copy("wasmer.lib", src=srclibdir, dst=dstlibdir, keep_path=False)
            self.copy("libwasmer.a", src=srclibdir, dst=dstlibdir, keep_path=False)
            replace_in_file(self, os.path.join(self.package_folder, "include", "wasm.h"),
                            "__declspec(dllimport)", "")

    def package_info(self):
        self.cpp_info.libs = ["wasmer"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread", "dl", "m"]
                if Version(self.version) >= "2.3.0":
                    self.cpp_info.system_libs.append("rt")
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["bcrypt", "userenv", "ws2_32"]
