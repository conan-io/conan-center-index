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
    no_copy_source = True

    @property
    def _sources_os_key(self):
        if self.settings.compiler == "Visual Studio":
            return "Windows"
        return str(self.settings.os)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        del self.settings.compiler.runtime

    def validate(self):
        try:
            self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os are not available")

        if (self.settings.compiler, self.settings.os) == ("gcc", "Windows"):
                raise ConanInvalidConfiguration("mingw is currently not supported")

    def package_id(self):
        del self.info.settings.compiler.version
        if self.settings.compiler == "clang":
            self.info.settings.compiler = "gcc"

    def build(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
                  destination=self.source_folder)

    def package(self):
        self.copy("*.h", src=os.path.join(self.source_folder, "include"), dst="include", keep_path=False)

        srclibdir = os.path.join(self.source_folder, "lib")
        if self.options.shared:
            self.copy("wasmer.dll", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmer.so*", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmtime.dylib", src=srclibdir,  dst="lib", keep_path=False)
        else:
            self.copy("wasmer.lib", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmer.a", src=srclibdir, dst="lib", keep_path=False)

        self.copy("LICENSE", dst="licenses", src=self.source_folder)

    def package_info(self):
        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.libs = ["wasmer.dll"]
            else:
                self.cpp_info.libs = ["wasmer"]
        else:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["WASM_API_EXTERN=", "WASI_API_EXTERN="]
            self.cpp_info.libs = ["wasmer"]

            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["ws2_32", "bcrypt", "advapi32", "userenv", "ntdll", "shell32", "ole32"]
            elif self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "m"]
