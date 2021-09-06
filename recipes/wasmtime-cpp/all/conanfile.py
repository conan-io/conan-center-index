from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException
import os
import shutil

required_conan_version = ">=1.33.0"

class WasmtimeCppConan(ConanFile):
    name = 'wasmtime-cpp'
    homepage = 'https://github.com/bytecodealliance/wasmtime-cpp'
    license = 'Apache-2.0'
    url = 'https://github.com/conan-io/conan-center-index'
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    topics = ("webassembly", "wasm", "wasi", "c++")
    settings = "os", "compiler", "arch"
    options = { "shared": [True, False] }
    default_options = { 'shared': False }
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16.8",
            "apple-clang": "9.4",
            "clang": "5.0",
            "gcc": "8.0"
        }

    @property
    def _sources_key(self):
        if self.settings.compiler == "Visual Studio":
            return "Windows"
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            return "MinGW"
        return str(self.settings.os)

    def configure(self):
        del self.settings.compiler.runtime

    def requirements(self):
        self.requires("wasmtime/0.29.0")

    def validate(self):
        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version[str(compiler)]
        try:
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {} !!"
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

        try:
            self.conan_data["sources"][self.version][self._sources_key][str(self.settings.arch)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][self._sources_key][str(self.settings.arch)], destination=self.source_folder, strip_root=True)

    def package(self):
        shutil.copytree(os.path.join(self.source_folder, "include"),
                        os.path.join(self.package_folder, "include"))

        self.copy('LICENSE', dst='licenses', src=self.source_folder)

    def package_info(self):
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.defines= ["/DWASM_API_EXTERN=", "/DWASI_API_EXTERN="]
