from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class WasmedgeConan(ConanFile):
    name = "wasmedge"
    description = ("WasmEdge is a lightweight, high-performance, and extensible WebAssembly runtime"
                "for cloud native, edge, and decentralized applications."
                "It powers serverless apps, embedded functions, microservices, smart contracts, and IoT devices.")
    topics = ("webassembly", "wasm", "wasi", "emscripten")
    license = "Apache-2.0"
    homepage = "https://github.com/WasmEdge/WasmEdge/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler",

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compiler_alias(self):
        return {
            "Visual Studio": "Visual Studio",
            "msvc": "Visual Studio",
        }.get(str(self.settings.compiler), "gcc")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        try:
            self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of version/os/arch/compiler are not available")

    def package_id(self):
        del self.info.settings.compiler.version
        self.info.settings.compiler = self._compiler_alias

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias][0],
                  destination=self._source_subfolder, strip_root=True)
        tools.download(filename="LICENSE",
                       **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)][self._compiler_alias][1])

    def package(self):
        self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)
        self.copy("*.inc", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)

        srclibdir = os.path.join(self._source_subfolder, "lib64" if self.settings.os == "Linux" else "lib")
        srcbindir = os.path.join(self._source_subfolder, "bin")

        self.copy("wasmedge_c.lib", src=srclibdir, dst="lib", keep_path=False)
        self.copy("wasmedge_c.dll", src=srcbindir, dst="bin", keep_path=False)
        self.copy("libwasmedge_c.so*", src=srclibdir, dst="lib", keep_path=False)
        self.copy("libwasmedge_c.dylib", src=srclibdir,  dst="lib", keep_path=False)

        self.copy("wasmedge*", src=srcbindir, dst="bin", keep_path=False)

        self.copy("LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["wasmedge_c"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
