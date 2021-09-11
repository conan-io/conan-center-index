import os
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
    options = {"fPIC": [True, False], "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}
    exports_sources = ["CMakeLists.txt", "patches/**"]

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            patch["base_path"] = self._source_subfolder
            tools.patch(**patch)

        if not self.options.get_safe("fPIC", True):
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
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
        if self.settings.os in ["Linux", "FreeBSD"]:
            component.system_libs = ["pthread"]
