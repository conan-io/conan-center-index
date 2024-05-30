import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class LibProtobufMutatorConan(ConanFile):
    name = "libprotobuf-mutator"
    description = "Library for structured fuzzing with protobuffers"
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

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "5",
            "apple-clang": "10",
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
        # Protobuf 5.* is not compatible as of v1.3
        self.requires("protobuf/4.25.3", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["LIB_PROTO_MUTATOR_TESTING"] = False
        tc.variables["LIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF"] = False
        tc.variables["LIB_PROTO_MUTATOR_WITH_ASAN"] = False
        tc.variables["LIB_PROTO_MUTATOR_FUZZER_LIBRARIES"] = ""
        if is_msvc(self):
            tc.variables["LIB_PROTO_MUTATOR_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
            # Should be added because of
            # https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-initonceexecuteonce
            tc.preprocessor_definitions["_WIN32_WINNT"] = "0x0600"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("protobuf", "cmake_file_name", "Protobuf")
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "include_directories(${PROTOBUF_INCLUDE_DIRS})",
                        "include_directories(${Protobuf_INCLUDE_DIRS})")
        rmdir(self, os.path.join(self.source_folder, "cmake", "external"))
        save(self, os.path.join(self.source_folder, "examples", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libprotobuf-mutator")

        self.cpp_info.components["protobuf-mutator"].libs = ["protobuf-mutator"]
        self.cpp_info.components["protobuf-mutator"].set_property("cmake_target_name", "libprotobuf-mutator::protobuf-mutator")
        self.cpp_info.components["protobuf-mutator"].includedirs.append(os.path.join("include", "libprotobuf-mutator"))
        self.cpp_info.components["protobuf-mutator"].requires = ["protobuf::libprotobuf"]

        self.cpp_info.components["protobuf-mutator-libfuzzer"].libs = ["protobuf-mutator-libfuzzer"]
        self.cpp_info.components["protobuf-mutator-libfuzzer"].set_property("cmake_target_name", "libprotobuf-mutator::protobuf-mutator-libfuzzer")
        self.cpp_info.components["protobuf-mutator-libfuzzer"].requires = ["protobuf-mutator"]
