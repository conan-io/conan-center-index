from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibProtobufMutatorConan(ConanFile):
    name = "libprotobuf-mutator"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libprotobuf-mutator"
    description = "A library to randomly mutate protobuffers."
    topics = ("test", "fuzzing", "protobuf")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("protobuf/3.17.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("Only clang allowed")
        if self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("Requires either compiler.libcxx=libstdc++11")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def _patch_sources(self):
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            """include_directories(${PROTOBUF_INCLUDE_DIRS})""",
            """include_directories(${protobuf_INCLUDE_DIRS})""")
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            """set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/external)""",
            """# (disabled by conan) set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/external)""")
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            """add_subdirectory(examples EXCLUDE_FROM_ALL)""",
            """# (disabled by conan) add_subdirectory(examples EXCLUDE_FROM_ALL)""")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["LIB_PROTO_MUTATOR_TESTING"] = "OFF"
        self._cmake.definitions["LIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF"] = "OFF"
        self._cmake.definitions["LIB_PROTO_MUTATOR_WITH_ASAN"] = "OFF"
        self._cmake.definitions["LIB_PROTO_MUTATOR_FUZZER_LIBRARIES"] = ""
        # todo: check option(LIB_PROTO_MUTATOR_MSVC_STATIC_RUNTIME "Link static runtime libraries" ON)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "OFF"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libprotobuf-mutator"
        self.cpp_info.names["cmake_find_package_multi"] = "libprotobuf-mutator"

        self.cpp_info.libs = ['protobuf-mutator-libfuzzer', 'protobuf-mutator']
        self.cpp_info.includedirs.append(os.path.join("include", "libprotobuf-mutator"))
