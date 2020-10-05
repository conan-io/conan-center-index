import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class PackioConan(ConanFile):
    name = "packio"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qchateau/packio"
    description = "An asynchronous msgpack-RPC and JSON-RPC library built on top of Boost.Asio."
    topics = ("rpc", "msgpack", "json", "asio", "async", "cpp17", "cpp20", "coroutines")
    settings = "compiler"
    no_copy_source = True
    options = {
        "standalone_asio": [True, False],
        "msgpack": [True, False],
        "nlohmann_json": [True, False],
    }
    default_options = {
        "standalone_asio": False,
        "msgpack": True,
        "nlohmann_json": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
        }

    def config_options(self):
        if tools.Version(self.version) < "1.2.0":
            del self.options.standalone_asio
        if tools.Version(self.version) < "2.0.0":
            del self.options.msgpack
            del self.options.nlohmann_json

    def requirements(self):
        if self.options.get_safe("msgpack") or tools.Version(self.version) < "2.0.0":
            self.requires("msgpack/3.2.1")

        if self.options.get_safe("nlohmann_json"):
            self.requires("nlohmann_json/3.9.1")

        if self.options.get_safe("standalone_asio"):
            self.requires("asio/1.16.1")
        else:
            self.requires("boost/1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "packio-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("packio requires C++17, which your compiler does not support.")
        else:
            self.output.warn("packio requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.get_safe("standalone_asio"):
            self.cpp_info.defines.append("PACKIO_STANDALONE_ASIO")
