from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54.0"


class LibProtobufMutatorConan(ConanFile):
    name = "libprotobuf-mutator"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libprotobuf-mutator"
    description = "A library to randomly mutate protobuffers."
    topics = ("test", "fuzzing", "protobuf")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "5",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.options.rm_safe("shared")
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Protobuf headers are required by public src/binary_format.h and
        self.requires("protobuf/4.25.3", transitive_headers=True)
        # Abseil headers are required by public src/field_instance.h
        self.requires("abseil/20240116.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        # Preserves Conan as dependency manager
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/external)",
            "",
        )
        # Fix libprotobuf-mutator.pc installation origin path
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "${CMAKE_BINARY_DIR}/libprotobuf-mutator.pc",
            "${CMAKE_CURRENT_BINARY_DIR}/libprotobuf-mutator.pc",
        )
        # Do not include examples when running CMake configure to avoid more dependencies
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "add_subdirectory(examples EXCLUDE_FROM_ALL)",
            "",
        )

    def generate(self):
        tc = VirtualBuildEnv(self)
        tc.generate()
        tc = CMakeToolchain(self)
        tc.variables["LIB_PROTO_MUTATOR_TESTING"] = False
        tc.variables["LIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF"] = False
        tc.variables["LIB_PROTO_MUTATOR_WITH_ASAN"] = False
        tc.variables["PKG_CONFIG_PATH"] = "share"
        if is_msvc(self):
            tc.variables["LIB_PROTO_MUTATOR_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["mutator"].libs = ["protobuf-mutator"]
        self.cpp_info.components["mutator"].set_property("cmake_target_name", "libprotobuf-mutator::protobuf-mutator")
        self.cpp_info.components["mutator"].includedirs.append("include/libprotobuf-mutator")
        self.cpp_info.components["mutator"].requires = ["protobuf::libprotobuf", "abseil::absl_strings"]

        self.cpp_info.components["fuzzer"].libs = ['protobuf-mutator-libfuzzer']
        self.cpp_info.components["fuzzer"].set_property("cmake_target_name", "libprotobuf-mutator::protobuf-mutator-libfuzzer")
        self.cpp_info.components["fuzzer"].includedirs.append("include/libprotobuf-mutator")
        self.cpp_info.components["fuzzer"].requires = ["mutator", "protobuf::libprotobuf"]
