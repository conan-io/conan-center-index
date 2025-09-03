from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class AsioGrpcConan(ConanFile):
    name = "asio-grpc"
    description = "Asynchronous gRPC with Asio/unified executors"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Tradias/asio-grpc"
    topics = ("cpp", "asynchronous", "grpc", "asio", "asynchronous-programming", "cpp17", "coroutine", "cpp20", "executors", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "backend": ["boost", "asio", "unifex"],
    }
    default_options = {
        "backend": "boost",
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "6",
            "apple-clang": "11",
        }

    def requirements(self):
        use_latest = Version(self.version) > "2.8"
        self.requires("grpc/1.67.1", transitive_headers=True, transitive_libs=True)
        if self.options.backend == "boost":
            version = "1.88.0" if use_latest else "1.83.0"
            self.requires(f"boost/{version}", transitive_headers=True)
        if self.options.backend == "asio":
            version = "1.32.0" if use_latest else "1.29.0"
            self.requires(f"asio/{version}", transitive_headers=True)
        if self.options.backend == "unifex":
            self.requires("libunifex/0.4.0", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        compiler_version = Version(self.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if Version(self.version) == "2.7.0" and self.settings.compiler == "gcc" and compiler_version.major == "11" and \
                compiler_version < "11.3":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc 11.0-11.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "asio-grpc*", os.path.join(self.package_folder, "lib", "cmake", "asio-grpc"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        build_modules = [os.path.join("lib", "cmake", "asio-grpc", "AsioGrpcProtobufGenerator.cmake")]

        self.cpp_info.requires = ["grpc::grpc++"]
        if self.options.backend == "boost":
            self.cpp_info.defines = ["AGRPC_BOOST_ASIO"]
            self.cpp_info.requires.append("boost::headers")
        if self.options.backend == "asio":
            self.cpp_info.defines = ["AGRPC_STANDALONE_ASIO"]
            self.cpp_info.requires.append("asio::asio")
        if self.options.backend == "unifex":
            self.cpp_info.defines = ["AGRPC_UNIFEX"]
            self.cpp_info.requires.append("libunifex::unifex")

        self.cpp_info.set_property("cmake_file_name", "asio-grpc")
        self.cpp_info.set_property("cmake_target_name", "asio-grpc::asio-grpc")
        self.cpp_info.set_property("cmake_build_modules", build_modules)
