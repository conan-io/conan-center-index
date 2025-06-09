import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get

class PackioConan(ConanFile):
    name = "packio"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qchateau/packio"
    description = "An asynchronous msgpack-RPC and JSON-RPC library built on top of Boost.Asio."
    topics = ("rpc", "msgpack", "json", "asio", "async", "cpp17", "cpp20", "coroutines")
    settings = "compiler"
    package_type = "header-library"
    no_copy_source = True
    options = {
        "standalone_asio": [True, False],
        "msgpack": [True, False],
        "nlohmann_json": [True, False],
        "boost_json": [True, False],
    }
    default_options = {
        "standalone_asio": False,
        "msgpack": True,
        "nlohmann_json": True,
        # boost_json no default value for boost_json, if not defined, derive from standalone_asio
    }

    def configure(self):
        # defaults to True if using boost.asio, False if using asio
        if self.options.get_safe("boost_json") is None:
            self.options.boost_json = not self.options.get_safe("standalone_asio", False)

    def requirements(self):
        if self.options.get_safe("msgpack"):
            self.requires("msgpack-cxx/7.0.0")

        if self.options.get_safe("nlohmann_json"):
            self.requires("nlohmann_json/3.9.1")

        if self.options.get_safe("boost_json") or not self.options.get_safe("standalone_asio"):
            self.requires("boost/1.83.0")

        if self.options.get_safe("standalone_asio"):
            self.requires("asio/1.18.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, "17")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"),dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.defines.append(f"PACKIO_STANDALONE_ASIO={1 if self.options.get_safe('standalone_asio') else 0}")
        self.cpp_info.defines.append(f"PACKIO_HAS_MSGPACK={1 if self.options.get_safe('msgpack') else 0}")
        self.cpp_info.defines.append(f"PACKIO_HAS_NLOHMANN_JSON={1 if self.options.get_safe('nlohmann_json') else 0}")
        self.cpp_info.defines.append(f"PACKIO_HAS_BOOST_JSON={1 if self.options.get_safe('boost_json') else 0}")
