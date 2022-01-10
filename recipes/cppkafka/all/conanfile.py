from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class CppKafkaConan(ConanFile):
    name = "cppkafka"
    description = "Modern C++ Apache Kafka client library (wrapper for librdkafka)"
    topics = ("librdkafka", "kafka")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/cppkafka"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    options = {
       "shared": [True, False],
       "multithreaded": [True, False]
    }
    default_options = {
        "shared": False,
        "multithreaded": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("librdkafka/1.8.2")

    def configure(self):
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version.value) < 14:
            raise Exception("cppkafka could not be built by MSVC <14")

    def configure_cmake(self):
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
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.system_libs = ['mswsock', 'ws2_32']
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ['pthread']
        if not self.options.shared:
            self.cpp_info.defines.append("CPPKAFKA_RDKAFKA_STATIC_LIB")
