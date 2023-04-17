from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class WasmtimeCppConan(ConanFile):
    name = 'wasmtime-cpp'
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    license = 'Apache-2.0'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/bytecodealliance/wasmtime-cpp'
    topics = ("webassembly", "wasm", "wasi", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "12",
            "clang": "12",
            "gcc": "10"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        version = str(self.version)
        version_map = {
            "0.35.0": "0.35.1",
            "0.39.0": "0.39.1",
            "1.0.0": "1.0.1",
            "6.0.0": "6.0.1",
        }
        self.requires(f"wasmtime/{version_map.get(version, version)}")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self,
            pattern="*.hh",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
