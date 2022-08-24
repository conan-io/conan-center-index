from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"

class WasmtimeCppConan(ConanFile):
    name = 'wasmtime-cpp'
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    license = 'Apache-2.0'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/bytecodealliance/wasmtime-cpp'
    topics = ("webassembly", "wasm", "wasi", "c++")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "apple-clang": "12.0",
            "clang": "12.0",
            "gcc": "10.0"
        }

    def requirements(self):
        version = str(self.version)
        if version == "0.35.0":
            version = "0.35.1"
        elif version == "0.39.0":
            version = "0.39.1"
        self.requires(f"wasmtime/{version}")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        compiler = self.settings.compiler
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        shutil.copytree(os.path.join(self.source_folder, "include"),
                        os.path.join(self.package_folder, "include"))

        self.copy('LICENSE', dst='licenses', src=self.source_folder)
