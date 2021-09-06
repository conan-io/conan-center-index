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
    exports_sources = "include/*"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "apple-clang": "9.4",
            "clang": "5.0",
            "gcc": "8.0"
        }

    def requirements(self):
        self.requires("wasmtime/0.29.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        shutil.copytree(os.path.join(self.source_folder, "include"),
                        os.path.join(self.package_folder, "include"))

        self.copy('LICENSE', dst='licenses', src=self.source_folder)
