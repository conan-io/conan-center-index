from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class WasmerConan(ConanFile):
    name = "wasmer"
    homepage = "https://github.com/wasmerio/wasmer/"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The leading WebAssembly Runtime supporting WASI and Emscripten"
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
        }.get(str(self.settings.compiler), "gcc")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                del self.settings.compiler.runtime

    def validate(self):
        try:
            self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of version/os/arch/compiler are not available")

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared Windows build of wasmer are non-working atm (no import libraries are available)")

        if self.settings.compiler == "Visual Studio":
            if not self.options.shared and self.settings.compiler.runtime != "MT":
                raise ConanInvalidConfiguration("wasmer is only available with compiler.runtime=MT")

    def package_id(self):
        del self.info.settings.compiler.version
        self.info.settings.compiler = self._compiler_alias

    def build(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias],
                  destination=self.source_folder)

    def package(self):
        self.copy("*.h", src=os.path.join(self.source_folder, "include"), dst="include", keep_path=False)

        srclibdir = os.path.join(self.source_folder, "lib")
        if self.options.shared:
            self.copy("wasmer.dll.lib", src=srclibdir, dst="lib", keep_path=False)  # FIXME: not available (yet)
            self.copy("wasmer.dll", src=srclibdir, dst="bin", keep_path=False)
            self.copy("libwasmer.so*", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmer.dylib", src=srclibdir,  dst="lib", keep_path=False)
        else:
            self.copy("wasmer.lib", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmer.a", src=srclibdir, dst="lib", keep_path=False)
            tools.replace_in_file(os.path.join(self.package_folder, "include", "wasm.h"),
                                  "__declspec(dllimport)", "")

        self.copy("LICENSE", dst="licenses", src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["wasmer"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread", "dl", "m"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["bcrypt", "userenv", "ws2_32"]
