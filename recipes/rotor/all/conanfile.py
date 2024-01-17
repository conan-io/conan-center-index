import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import get, rmdir, copy
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout

required_conan_version = ">=1.53.0"

class RotorConan(ConanFile):
    name = "rotor"
    description = "Event loop friendly C++ actor micro-framework, supervisable"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/basiliscos/cpp-rotor"
    topics = ("concurrency", "actor-framework", "actors", "actor-model", "erlang", "supervising", "supervisor")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "enable_asio": [True, False],
        "enable_thread": [True, False],
        "multithreading": [True, False],  # enables multithreading support
        "enable_ev": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "enable_asio": False,
        "enable_thread": False,
        "multithreading": True,
        "enable_ev": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.26":
            del self.options.enable_ev

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0", transitive_headers=True)
        if self.options.get_safe("enable_ev", False):
            self.requires("libev/4.33")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.shared and Version(self.version) < "0.23":
            raise ConanInvalidConfiguration("shared option is available from v0.23")

    def build_requirements(self):
        if Version(self.version) >= "0.26":
            self.tool_requires("cmake/[>=3.23 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BOOST_ASIO"] = self.options.enable_asio
        tc.variables["BUILD_THREAD"] = self.options.enable_thread
        tc.variables["BUILD_THREAD_UNSAFE"] = not self.options.multithreading
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) >= "0.26":
            tc.variables["BUILD_EV"] = self.options.enable_ev
        tc.generate()
        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["core"].libs = ["rotor"]
        self.cpp_info.components["core"].requires = ["boost::date_time", "boost::system", "boost::regex"]

        if not self.options.multithreading:
            self.cpp_info.components["core"].defines.append("BUILD_THREAD_UNSAFE")

        if self.options.enable_asio:
            self.cpp_info.components["asio"].libs = ["rotor_asio"]
            self.cpp_info.components["asio"].requires = ["core"]

        if self.options.enable_thread:
            self.cpp_info.components["thread"].libs = ["rotor_thread"]
            self.cpp_info.components["thread"].requires = ["core"]

        if self.options.get_safe("enable_ev", False):
            self.cpp_info.components["ev"].libs = ["rotor_ev"]
            self.cpp_info.components["ev"].requires = ["core", "libev::libev"]
