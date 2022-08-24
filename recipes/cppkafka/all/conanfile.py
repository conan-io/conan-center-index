from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class CppKafkaConan(ConanFile):
    name = "cppkafka"
    description = "Modern C++ Apache Kafka client library (wrapper for librdkafka)"
    topics = ("librdkafka", "kafka")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/cppkafka"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
       "shared": [True, False],
       "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("librdkafka/1.8.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CPPKAFKA_BUILD_SHARED"] = self.options.shared
        cmake.definitions["CPPKAFKA_DISABLE_TESTS"] = True
        cmake.definitions["CPPKAFKA_DISABLE_EXAMPLES"] = True
        cmake.definitions["CPPKAFKA_RDKAFKA_STATIC_LIB"] = False # underlying logic is useless
        if self.settings.os == "Windows":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-DNOMINMAX"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CppKafka")
        self.cpp_info.set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.set_property("pkg_config_name", "cppkafka")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_cppkafka"].libs = ["cppkafka"]
        self.cpp_info.components["_cppkafka"].requires = ["boost::headers", "librdkafka::librdkafka"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.components["_cppkafka"].system_libs = ["mswsock", "ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_cppkafka"].system_libs = ["pthread"]
        if not self.options.shared:
            self.cpp_info.components["_cppkafka"].defines.append("CPPKAFKA_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CppKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "CppKafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package_multi"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.components["_cppkafka"].set_property("pkg_config_name", "cppkafka")
