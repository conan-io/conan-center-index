import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir, copy
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout

required_conan_version = ">=1.52.0"

class RotorConan(ConanFile):
    name = "rotor"
    license = "MIT"
    homepage = "https://github.com/basiliscos/cpp-rotor"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "Event loop friendly C++ actor micro-framework, supervisable"
    )
    topics = ("concurrency", "actor-framework", "actors", "actor-model", "erlang", "supervising", "supervisor")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "enable_asio": [True, False],
        "enable_thread": [True, False],
        "multithreading": [True, False],  # enables multithreading support
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "enable_asio": False,
        "enable_thread": False,
        "multithreading": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def requirements(self):
        self.requires("boost/1.81.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BOOST_ASIO"] = self.options.enable_asio
        tc.variables["BUILD_THREAD"] = self.options.enable_thread
        tc.variables["BUILD_THREAD_UNSAFE"] = not self.options.multithreading
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                f"{self.ref} recipe lacks information about the {compiler} compiler standard version support")
            self.output.warn(
                f"{self.ref} requires a compiler that supports at least C++{minimal_cpp_standard}")
            return

        compiler_version = Version(self.settings.compiler.version)
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(f"{self.ref} requires a compiler that supports at least C++{minimal_cpp_standard}")

        if self.options.shared and Version(self.version) < "0.23":
            raise ConanInvalidConfiguration("shared option is available from v0.23")


    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "rotor"
