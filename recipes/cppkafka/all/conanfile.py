from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < 6:
            raise ConanInvalidConfiguration("cppkafka could not be built by gcc <6")
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("cppkafka could not be built by MSVC <14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        opts = dict()
        opts["RDKAFKA_LIBRARY"] = self.deps_cpp_info["librdkafka"].rootpath
        opts["RDKAFKA_INCLUDE_DIR"] = self.deps_cpp_info["librdkafka"].rootpath + "/include"
        cmake.definitions["CPPKAFKA_BUILD_SHARED"] = self.options.shared
        cmake.definitions["CPPKAFKA_BOOST_USE_MULTITHREADED"] = self.options.multithreaded
        cmake.definitions["CPPKAFKA_RDKAFKA_STATIC_LIB"] = not self.deps_cpp_info["librdkafka"].shared
        cmake.configure(defs=opts, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
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

    def package_info(self):
        self.cpp_info.libs = ["cppkafka"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.system_libs = ['mswsock', 'ws2_32']
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ['pthread']
        if not self.deps_cpp_info["librdkafka"].shared:
            self.cpp_info.defines.append("CPPKAFKA_RDKAFKA_STATIC_LIB")
