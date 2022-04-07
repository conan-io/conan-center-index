from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"

class CppKafkaConan(ConanFile):
    name = "cppkafka"
    description = "Modern C++ Apache Kafka client library (wrapper for librdkafka)"
    topics = ("librdkafka", "kafka")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/cppkafka"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    options = {
       "shared": [True, False],
       "fPIC": [True, False],
       "multithreaded": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
    }

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
        self.options["librdkafka"].shared = self.options.shared

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
        cmake.definitions["CPPKAFKA_BOOST_USE_MULTITHREADED"] = self.options.multithreaded
        cmake.definitions["CPPKAFKA_RDKAFKA_STATIC_LIB"] = not self.deps_cpp_info["librdkafka"].shared

        cxx_flags = list()
        if self.settings.get_safe("compiler.libcxx") == "libstdc++":
            cxx_flags.append("-D_GLIBCXX_USE_CXX11_ABI=0")
        elif self.settings.get_safe("compiler.libcxx") == "libstdc++11":
            cxx_flags.append("-D_GLIBCXX_USE_CXX11_ABI=1")
        if not self.options.shared:
            cxx_flags.append("-DCPPKAFKA_STATIC")

        # disable max/min in Windows.h
        if self.settings.os == "Windows":
            cxx_flags.append("-DNOMINMAX")

        if len(cxx_flags) > 0:
            cmake.definitions["CMAKE_CXX_FLAGS"] = ' '.join(cxx_flags)

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} \"${CMAKE_CURRENT_SOURCE_DIR}/cmake/\")", "")
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
        self.cpp_info.libs = ["cppkafka"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.system_libs = ['mswsock', 'ws2_32']
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ['pthread']
        if not self.deps_cpp_info["librdkafka"].shared:
            self.cpp_info.defines.append("CPPKAFKA_RDKAFKA_STATIC_LIB")
        if self.options.shared == False:
            self.cpp_info.defines.append("CPPKAFKA_STATIC")

