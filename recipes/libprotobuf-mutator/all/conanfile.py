from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


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
        self.requires("protobuf/[>=4.25.3 <7]", transitive_headers=True)
        # Abseil headers are required by public src/field_instance.h
        self.requires("abseil/[*]") # use version from protobuf

    def validate(self):
        min_cppstd = "17" if Version(self.dependencies["protobuf"].ref.version) >= "6.30" else "14"
        check_min_cppstd(self, min_cppstd)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIB_PROTO_MUTATOR_TESTING"] = False
        tc.cache_variables["LIB_PROTO_MUTATOR_EXAMPLES"] = False
        tc.cache_variables["LIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF"] = False
        tc.cache_variables["LIB_PROTO_MUTATOR_WITH_ASAN"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_LibLZMA"] = True # only needed for examples

        if is_msvc(self):
            tc.cache_variables["LIB_PROTO_MUTATOR_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("protobuf", "cmake_additional_variables_prefixes", ["PROTOBUF", "Protobuf"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
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
