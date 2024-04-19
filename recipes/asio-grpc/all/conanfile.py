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
    description = "Asynchronous gRPC with Asio/unified executors"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Tradias/asio-grpc"
    topics = ("cpp", "asynchronous", "grpc", "asio", "asynchronous-programming", "cpp17", "coroutine", "cpp20", "executors", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "backend": ["boost", "asio", "unifex"],
        "local_allocator": ["auto", "memory_resource", "boost_container", "recycling_allocator"],
    }
    default_options = {
        "backend": "boost",
        "local_allocator": "auto",
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

    def configure(self):
        self._local_allocator_option = self.options.local_allocator
        if self._local_allocator_option == "auto":
            libcxx = self.settings.compiler.get_safe("libcxx")
            compiler_version = Version(self.settings.compiler.version)
            prefer_boost_container = libcxx and str(libcxx) == "libc++" or \
                (self.settings.compiler == "gcc" and compiler_version < "9")  or \
                (self.settings.compiler == "clang" and compiler_version < "12" and libcxx and str(libcxx) == "libstdc++")
            self._local_allocator_option = "boost_container" if prefer_boost_container else "memory_resource"
        if self._local_allocator_option == "recycling_allocator" and self.options.backend == "unifex":
            raise ConanInvalidConfiguration(f"{self.name} 'recycling_allocator' cannot be used in combination with the 'unifex' backend.")

    def requirements(self):
        self.requires("grpc/1.54.3", transitive_libs=True)
        if self._local_allocator_option == "boost_container" or self.options.backend == "boost":
            self.requires("boost/1.83.0", transitive_headers=True)
        if self.options.backend == "asio":
            self.requires("asio/1.29.0", transitive_headers=True)
        if self.options.backend == "unifex":
            self.requires("libunifex/0.4.0")

    def package_id(self):
        self.info.clear()
        self.info.options.local_allocator = self._local_allocator_option

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
        else:
            self.output.warning(
                f"{self.name} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports"
                f" C++{self._min_cppstd}."
            )
        if Version(self.version) == "2.7.0" and self.settings.compiler == "gcc" and compiler_version.major == "11" and \
            compiler_version < "11.3":
            raise ConanInvalidConfiguration(f"{self.ref} does not support gcc 11.0-11.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASIO_GRPC_USE_BOOST_CONTAINER"] = self._local_allocator_option == "boost_container"
        tc.variables["ASIO_GRPC_USE_RECYCLING_ALLOCATOR"] = self._local_allocator_option == "recycling_allocator"
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

        if self._local_allocator_option == "boost_container":
            self.cpp_info.requires.append("boost::container")

        self.cpp_info.set_property("cmake_file_name", "asio-grpc")
        self.cpp_info.set_property("cmake_target_name", "asio-grpc::asio-grpc")
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = build_modules
        self.cpp_info.build_modules["cmake_find_package_multi"] = build_modules
