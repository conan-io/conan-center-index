import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibProtobufMutatorConan(ConanFile):
    name = "libprotobuf-mutator"
    description = "A library to randomly mutate protobuffers."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libprotobuf-mutator"
    topics = ("test", "fuzzing", "protobuf")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("protobuf/3.21.12", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("Requires compiler.libcxx=libstdc++11")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIB_PROTO_MUTATOR_TESTING"] = "OFF"
        tc.variables["LIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF"] = "OFF"
        tc.variables["LIB_PROTO_MUTATOR_WITH_ASAN"] = "OFF"
        tc.variables["LIB_PROTO_MUTATOR_FUZZER_LIBRARIES"] = ""
        # todo: check option(LIB_PROTO_MUTATOR_MSVC_STATIC_RUNTIME "Link static runtime libraries" ON)
        if is_msvc(self):
            # Should be added because of
            # https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-initonceexecuteonce
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0600"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "include_directories(${PROTOBUF_INCLUDE_DIRS})",
            "include_directories(${protobuf_INCLUDE_DIRS})",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/external)",
            "# (disabled by conan) set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/external)",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "add_subdirectory(examples EXCLUDE_FROM_ALL)",
            "# (disabled by conan) add_subdirectory(examples EXCLUDE_FROM_ALL)",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "OFF"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["protobuf-mutator-libfuzzer", "protobuf-mutator"]
        self.cpp_info.includedirs.append(os.path.join("include", "libprotobuf-mutator"))
