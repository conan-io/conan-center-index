from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
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

    generators = "cmake", "cmake_find_package_multi"

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

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "6",
            "clang": "4",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "{}/{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version,))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{}/{} requires C++14, which your compiler does not support.".format(self.name, self.version,))

        if self.settings.compiler in ["clang", "apple-clang"] and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration(
                "{}/{} doesn't support {} with libc++".format(self.name, self.version, self.settings.compiler))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CPPKAFKA_BUILD_SHARED"] = self.options.shared
        cmake.definitions["CPPKAFKA_DISABLE_TESTS"] = True
        cmake.definitions["CPPKAFKA_DISABLE_EXAMPLES"] = True
        cmake.definitions["CPPKAFKA_RDKAFKA_STATIC_LIB"] = False # underlying logic is useless

        cxx_flags = list()
        # disable max/min in Windows.h
        if self.settings.os == "Windows":
            cxx_flags.append("-DNOMINMAX")

        if len(cxx_flags) > 0:
            cmake.definitions["CMAKE_CXX_FLAGS"] = ' '.join(cxx_flags)

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CppKafka")
        self.cpp_info.set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.set_property("pkg_config_name", "cppkafka")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_cppkafka"].libs = ["cppkafka"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.components["_cppkafka"].system_libs = ["mswsock", "ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_cppkafka"].system_libs = ["pthread"]
        if not self.deps_cpp_info["librdkafka"].shared:
            self.cpp_info.components["_cppkafka"].defines.append("CPPKAFKA_RDKAFKA_STATIC_LIB")
        if self.options.shared == False:
            self.cpp_info.components["_cppkafka"].defines.append("CPPKAFKA_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CppKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "CppKafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package_multi"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.components["_cppkafka"].set_property("pkg_config_name", "cppkafka")
