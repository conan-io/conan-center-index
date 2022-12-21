from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class PackioConan(ConanFile):
    name = "packio"
    license = "MPL-2.0"
    description = "An asynchronous msgpack-RPC and JSON-RPC library built on top of Boost.Asio."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qchateau/packio"
    topics = ("rpc", "msgpack", "json", "asio", "async", "cpp17", "cpp20", "coroutines")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "standalone_asio": [True, False],
        "msgpack": [True, False],
        "nlohmann_json": [True, False],
        "boost_json": [True, False, "default"],
    }
    default_options = {
        "standalone_asio": False,
        "msgpack": True,
        "nlohmann_json": True,
        "boost_json": "default",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "msvc": 192,
            "Visual Studio": 16,
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if Version(self.version) < "1.2.0":
            del self.options.standalone_asio
        if Version(self.version) < "2.0.0":
            del self.options.msgpack
            del self.options.nlohmann_json
        if Version(self.version) < "2.1.0":
            del self.options.boost_json

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("msgpack") or Version(self.version) < "2.0.0":
            self.requires("msgpack/3.3.0")

        if self.options.get_safe("nlohmann_json"):
            self.requires("nlohmann_json/3.9.1")

         # defaults to True if using boost.asio, False if using asio
        if self.options.get_safe("boost_json") == "default":
            self.options.boost_json = not self.options.standalone_asio

        if self.options.get_safe("boost_json") or not self.options.get_safe("standalone_asio"):
            self.requires("boost/1.80.0")

        if self.options.get_safe("standalone_asio"):
            self.requires("asio/1.24.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        else:
            self.output.warn(f"{self.ref} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if Version(self.version) < "2.1.0":
            if self.options.get_safe("standalone_asio"):
                self.cpp_info.defines.append("PACKIO_STANDALONE_ASIO")
        else:
            # Starting from 2.1.0, preprocessor defines can be defined to 0 to force-disable
            self.cpp_info.defines.append(f"PACKIO_STANDALONE_ASIO={1 if self.options.get_safe('standalone_asio') else 0}")
            self.cpp_info.defines.append(f"PACKIO_HAS_MSGPACK={1 if self.options.get_safe('msgpack') else 0}")
            self.cpp_info.defines.append(f"PACKIO_HAS_NLOHMANN_JSON={1 if self.options.get_safe('nlohmann_json') else 0}")
            self.cpp_info.defines.append(f"PACKIO_HAS_BOOST_JSON={1 if self.options.get_safe('boost_json') else 0}")
