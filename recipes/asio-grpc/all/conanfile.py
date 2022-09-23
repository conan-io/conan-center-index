from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class AsioGrpcConan(ConanFile):
    name = "asio-grpc"
    description = ("Asynchronous gRPC with Asio/unified executors")
    homepage = "https://github.com/Tradias/asio-grpc"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("cpp", "asynchronous", "grpc", "asio", "asynchronous-programming", "cpp17", "coroutine", "cpp20", "executors")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "backend": ["boost", "asio", "unifex"],
        "use_boost_container": ["auto", True, False],
    }
    default_options = {
        "backend": "boost",
        "use_boost_container": "auto",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "11",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, which your compiler does not support.")
        else:
            self.output.warn(f"{self.name} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")

    def configure(self):
        if self.options.use_boost_container == "auto":
            libcxx = self.settings.compiler.get_safe("libcxx")
            compiler_version = Version(self.settings.compiler.version)
            self.options.use_boost_container = libcxx and str(libcxx) == "libc++" or \
                (self.settings.compiler == "gcc" and compiler_version < "9")  or \
                (self.settings.compiler == "clang" and compiler_version < "12" and libcxx and str(libcxx) == "libstdc++")

    def requirements(self):
        self.requires("grpc/1.48.0")
        if self.options.use_boost_container or self.options.backend == "boost":
            self.requires("boost/1.79.0")
        if self.options.backend == "asio":
            self.requires("asio/1.24.0")
        if self.options.backend == "unifex":
            self.requires("libunifex/cci.20220430")

    def package_id(self):
        self.info.clear()
        self.info.options.use_boost_container = self.options.use_boost_container

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASIO_GRPC_USE_BOOST_CONTAINER"] = self.options.use_boost_container
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
        build_modules = [os.path.join("lib", "cmake", "asio-grpc", "AsioGrpcProtobufGenerator.cmake")]
        
        self.cpp_info.requires = ["grpc::grpc++_unsecure"]
        if self.options.backend == "boost":
            self.cpp_info.defines = ["AGRPC_BOOST_ASIO"]
            self.cpp_info.requires.append("boost::headers")
        if self.options.backend == "asio":
            self.cpp_info.defines = ["AGRPC_STANDALONE_ASIO"]
            self.cpp_info.requires.append("asio::asio")
        if self.options.backend == "unifex":
            self.cpp_info.defines = ["AGRPC_UNIFEX"]
            self.cpp_info.requires.append("libunifex::unifex")

        if self.options.use_boost_container:
            self.cpp_info.requires.append("boost::container")

        self.cpp_info.set_property("cmake_file_name", "asio-grpc")
        self.cpp_info.set_property("cmake_target_name", "asio-grpc::asio-grpc")
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = build_modules
        self.cpp_info.build_modules["cmake_find_package_multi"] = build_modules
