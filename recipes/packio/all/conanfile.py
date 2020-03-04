import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class PackioConan(ConanFile):
    name = "packio"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qchateau/packio"
    description = "An asynchronous msgpack-RPC library built on top of Boost.Asio."
    topics = ("rpc", "msgpack", "asio", "async", "cpp17")
    settings = "compiler"
    no_copy_source = True
    requires = [
        "msgpack/3.2.1",
        "boost/1.72.0",
    ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _supports_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 16)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "packio-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("packio requires C++17 support")

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
