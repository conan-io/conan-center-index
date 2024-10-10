import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.51.1"


class PackioConan(ConanFile):
    name = "packio"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/qchateau/packio"
    description = "An asynchronous msgpack-RPC and JSON-RPC library built on top of Boost.Asio."
    topics = ("rpc", "msgpack", "json", "asio", "async", "cpp17", "cpp20", "coroutines")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
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
        return "17"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "2.4.0":
            return {
                "apple-clang": "10",
                "clang": "6",
                "gcc": "7",
                "Visual Studio": "16",
                "msvc": "192",
            }
        return {
            "apple-clang": "13",
            "clang": "11",
            "gcc": "9",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    @property
    def _use_boost_json(self):
        # defaults to True if using boost.asio, False if using asio
        if self.options.boost_json == "default":
            return not self.options.standalone_asio
        return self.options.boost_json

    def requirements(self):
        if self.options.msgpack:
            self.requires("msgpack-cxx/6.1.1")
        if self.options.nlohmann_json:
            self.requires("nlohmann_json/3.11.3")
        if self._use_boost_json or not self.options.standalone_asio:
            self.requires("boost/1.83.0")
        if self.options.standalone_asio:
            self.requires("asio/1.31.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        apply_conandata_patches(self)
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Preprocessor defines can be defined to 0 to force-disable
        self.cpp_info.defines = [
            f"PACKIO_STANDALONE_ASIO={1 if self.options.standalone_asio else 0}",
            f"PACKIO_HAS_MSGPACK={1 if self.options.msgpack else 0}",
            f"PACKIO_HAS_NLOHMANN_JSON={1 if self.options.nlohmann_json else 0}",
            f"PACKIO_HAS_BOOST_JSON={1 if self._use_boost_json else 0}",
        ]
