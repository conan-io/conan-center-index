from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException
import os


class WasmtimeConan(ConanFile):
    name = 'wasmtime'
    homepage = 'https://github.com/bytecodealliance/wasmtime'
    license = 'Apache-2.0'
    url = 'https://github.com/conan-io/conan-center-index'
    description = "Standalone JIT-style runtime for WebAssembly, using Cranelift"
    topics = ("webassembly", "wasm", "wasi")
    settings = "os", "compiler", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "apple-clang": "9.4",
            "clang": "3.3",
            "gcc": "4.9.4"
        }

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version[str(compiler)]
        try:
            if tools.Version(compiler.version) < min_version:
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
            self.conan_data["sources"][self.version][str(self.settings.os)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)], destination=self._source_subfolder, strip_root=True)

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
        elif self.settings.os == 'Linux':
            self.cpp_info.system_libs = ['pthread', 'dl', 'm']
