from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.files import get, copy, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.53.0"

class WasmerConan(ConanFile):
    name = "wasmer"
    description = "The leading WebAssembly Runtime supporting WASI and Emscripten"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wasmerio/wasmer/"
    topics = ("webassembly", "wasm", "wasi", "emscripten")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    @property
    def _compiler_alias(self):
        return {
            "Visual Studio": "msvc",
            "msvc": "msvc",
        }.get(str(self.info.settings.compiler), "gcc")

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
            raise ConanInvalidConfiguration(f"Shared Windows build of {self.ref} are non-working atm (no import libraries are available)")

        if self.settings.os == "Linux" and self.options.shared and "2.3.0" <= Version(self.version):
            raise ConanInvalidConfiguration(f"Shared Linux build of {self.ref} are not working. It requires glibc >= 2.25")

        if is_msvc(self) and not self.options.shared and not is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} is only available with compiler.runtime=static")

    def package_id(self):
        del self.info.settings.compiler.version
        self.info.settings.compiler = self._compiler_alias

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version][str(self.info.settings.os)][str(self.info.settings.arch)][self._compiler_alias]
        )

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

        srclibdir = os.path.join(self.source_folder, "lib")
        dstlibdir = os.path.join(self.package_folder, "lib")
        dstbindir = os.path.join(self.package_folder, "bin")
        if self.options.shared:
            copy(self, pattern="wasmer.dll.lib", dst=dstlibdir, src=srclibdir)  # FIXME: not available (yet)
            copy(self, pattern="wasmer.dll", dst=dstbindir, src=srclibdir)
            copy(self, pattern="libwasmer.so*", dst=dstlibdir, src=srclibdir)
            copy(self, pattern="libwasmer.dylib", dst=dstlibdir, src=srclibdir)
        else:
            copy(self, pattern="wasmer.lib", dst=dstlibdir, src=srclibdir)
            copy(self, pattern="libwasmer.a", dst=dstlibdir, src=srclibdir)
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
            elif is_apple_os(self) and Version(self.version) >= "3.2.0":
                self.cpp_info.frameworks = ["Security"]
