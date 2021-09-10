from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class NsyncConan(ConanFile):
    name = "nsync"
    homepage = "https://github.com/google/nsync"
    description = "Library that exports various synchronization primitive"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("c", "thread", "multithreading", "google")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt"]


    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NSYNC_ENABLE_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "nsync"
        self.cpp_info.filenames["cmake_find_package_multi"] = "nsync"
        self.cpp_info.names["cmake_find_package"] = "nsync"
        self.cpp_info.names["cmake_find_package_multi"] = "nsync"

        nsync_c = self.cpp_info.components["nsync_c"]
        nsync_c.name = "nsync_c"
        nsync_c.libs = ["nsync"]
        nsync_c.names["cmake_find_package"] = "nsync_c"
        nsync_c.names["cmake_find_package_multi"] = "nsync_c"
        nsync_c.names["pkg_config"] = "nsync"
        self._add_pthread_dep(nsync_c)

        nsync_cpp = self.cpp_info.components["nsync_cpp"]
        nsync_cpp.name = "nsync_cpp"
        nsync_cpp.libs = ["nsync_cpp"]
        nsync_cpp.names["cmake_find_package"] = "nsync_cpp"
        nsync_cpp.names["cmake_find_package_multi"] = "nsync_cpp"
        nsync_cpp.names["pkg_config"] = "nsync_cpp"
        self._add_pthread_dep(nsync_cpp)

    def _add_pthread_dep(self, component):
        if self.settings.os == "Linux":
            component.system_libs = ["pthread"]
            component.cxxflags.append("-pthread")
            component.exelinkflags.append("-pthread")
            component.sharedlinkflags.append("-pthread")
