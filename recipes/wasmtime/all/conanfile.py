from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os
import shutil

required_conan_version = ">=1.33.0"


class WasmtimeConan(ConanFile):
    name = "wasmtime"
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bytecodealliance/wasmtime"
    topics = ("webassembly", "wasm", "wasi")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "apple-clang": "9.4",
            "clang": "3.3",
            "gcc": "5.1"
        }

    @property
    def _sources_os_key(self):
        if is_msvc(self):
            return "Windows"
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            return "MinGW"
        return str(self.settings.os)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        del self.settings.compiler.runtime

    def validate(self):
        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version[str(compiler)]
        try:
            if tools.scm.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C{} features which are not supported by compiler {} {} !!"
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

        try:
            self.conan_data["sources"][self.version][self._sources_os_key][str(self.settings.arch)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os are not available")

        if tools.scm.Version(self.version) <= "0.29.0":
            if (self.settings.compiler, self.settings.os) == ("gcc", "Windows") and self.options.shared:
                # https://github.com/bytecodealliance/wasmtime/issues/3168
                raise ConanInvalidConfiguration("Shared mingw is currently not possible")

    def package_id(self):
        del self.info.settings.compiler.version
        if self.settings.compiler == "clang":
            self.info.settings.compiler = "gcc"

    def build(self):
        # This is packaging binaries so the download needs to be in build
        tools.files.get(self, **self.conan_data["sources"][self.version][self._sources_os_key][str(self.settings.arch)],
                  destination=self.source_folder, strip_root=True)

    def package(self):
        shutil.copytree(os.path.join(self.source_folder, "include"),
                        os.path.join(self.package_folder, "include"))

        srclibdir = os.path.join(self.source_folder, "lib")
        if self.options.shared:
            self.copy("wasmtime.dll.lib", src=srclibdir, dst="lib", keep_path=False)
            self.copy("wasmtime.dll", src=srclibdir, dst="bin", keep_path=False)
            self.copy("libwasmtime.dll.a", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmtime.so*", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmtime.dylib", src=srclibdir,  dst="lib", keep_path=False)
        else:
            self.copy("wasmtime.lib", src=srclibdir, dst="lib", keep_path=False)
            self.copy("libwasmtime.a", src=srclibdir, dst="lib", keep_path=False)

        self.copy("LICENSE", dst="licenses", src=self.source_folder)

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
