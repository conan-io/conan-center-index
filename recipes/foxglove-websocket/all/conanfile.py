from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class FoxgloveWebSocketConan(ConanFile):
    name = "foxglove-websocket"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/ws-protocol"
    description = "A C++ server implementation of the Foxglove WebSocket Protocol"
    license = "MIT"
    topics = ("foxglove", "websocket")

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16.9",
            "msvc": "191",
            "gcc": "9",
            "clang": "9",
            "apple-clang": "12",
        }

    @property
    def _source_package_path(self):
        return os.path.join(self.source_folder, "tarball", "cpp", "foxglove-websocket")

    def source(self):
        tmp_folder = "tarball"
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=tmp_folder)
        copy(self, "*", src=os.path.join(self.source_folder, tmp_folder, "cpp", "foxglove-websocket"), dst=self.source_folder)
        copy(self, "LICENSE", src=tmp_folder, dst=self.source_folder)
        rmdir(self, tmp_folder)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def requirements(self):
        self.requires("nlohmann_json/3.10.5", transitive_headers=True)
        self.requires("websocketpp/0.8.2")

    def layout(self):
        if self.version >= Version("1.0.0"):
            cmake_layout(self, src_folder="src")

    def generate(self):
        if self.version >= Version("1.0.0"):
            tc = CMakeToolchain(self)
            tc.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options["websocketpp"].asio = "standalone"

        if self.version < Version("1.0.0"):
            # Header only library
            self.options.rm_safe("shared")
            self.options.rm_safe("fPIC")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def build(self):
        if self.version >= Version("1.0.0"):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        if self.version >= Version("1.0.0"):
            cmake = CMake(self)
            cmake.install()
        else:
            copy(self, "include/*.hpp", self.source_folder, self.package_folder, keep_path=True)
            copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        if self.version >= Version("1.0.0"):
            self.cpp_info.libs = ["foxglove_websocket"]

    def package_id(self):
        if self.version < Version("1.0.0"):
            # Haeder only library. Can have the same package ID as there is no ABI incompatibility.
            self.info.clear()
