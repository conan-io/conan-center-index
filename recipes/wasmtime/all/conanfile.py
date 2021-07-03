from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException
import os


class WasmtimeConan(ConanFile):
    name = 'wasmtime'
    homepage = 'https://github.com/bytecodealliance/wasmtime'
    license = 'Apache License 2.0'
    url = 'https://github.com/conan-io/conan-center-index'
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    topics = ("webassembly", "wasm", "wasi")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    exports_sources = ['CMakeLists.txt', 'patches/*']

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        try:
            if self.settings.arch == "armv8" and self.settings.os == "Android":
                os_name = "Linux"
            else:
                os_name = str(self.settings.os)

            archive_ext = "zip" if os_name == "Windows" else "tar.xz"
            url = f"https://github.com/bytecodealliance/wasmtime/releases/download/v{self.version}/wasmtime-v{self.version}-{self.settings.arch}-{os_name.lower()}-c-api.{archive_ext}"
            tools.get(url, strip_root=True, destination=self._source_subfolder)
        except:
            raise Exception("Binary does not exist for these settings")

    def package(self):
        include_path = os.path.join(self._source_subfolder, 'include')
        self.copy('*.h', dst='include', src=include_path)
        self.copy('*.hh', dst='include', src=include_path)
        self.copy('*.hpp', dst='include', src=include_path)

        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='bin', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "wasmtime"
        self.cpp_info.names["cmake_find_multi_package"] = "wasmtime"
        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.libs = ["wasmtime.dll"]
            else:
                self.cpp_info.libs = ["wasmtime"]
        else:
            if self.settings.os == "Windows":
                self.cpp_info.defines= ["/DWASM_API_EXTERN=", "/DWASI_API_EXTERN="]
            self.cpp_info.libs = ["wasmtime"]

        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ['ws2_32', 'bcrypt', 'advapi32', 'userenv', 'ntdll', 'shell32', 'ole32']
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs = ['pthread', 'dl', 'm']
