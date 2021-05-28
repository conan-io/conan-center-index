from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class LibcdsConan(ConanFile):
    name = "libcds"
    description = "C++11 library of Concurrent Data Structures."
    license = "BSL-1.0"
    topics = ("conan", "libcds", "concurrent", "lock-free", "containers", "hazard-pointer", "rcu")
    homepage = "https://github.com/khizmax/libcds"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("boost/1.76.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.definitions["WITH_TESTS_COVERAGE"] = False
        self._cmake.definitions["WITH_BOOST_ATOMIC"] = False
        self._cmake.definitions["WITH_ASAN"] = False
        self._cmake.definitions["WITH_TSAN"] = False
        self._cmake.definitions["ENABLE_UNIT_TEST"] = False
        self._cmake.definitions["ENABLE_STRESS_TEST"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibCDS"
        self.cpp_info.names["cmake_find_package_multi"] = "LibCDS"
        cmake_target = "cds" if self.options.shared else "cds-s"
        self.cpp_info.components["_libcds"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_libcds"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_libcds"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["_libcds"].defines = ["CDS_BUILD_STATIC_LIB"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_libcds"].system_libs = ["pthread"]
        if self.settings.compiler in ["gcc", "clang", "apple-clang"] and self.settings.arch == "x86_64":
            self.cpp_info.components["_libcds"].cxxflags = ["-mcx16"]
        self.cpp_info.components["_libcds"].requires = ["boost::boost"]
