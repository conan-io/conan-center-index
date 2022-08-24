import os
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


class NsyncConan(ConanFile):
    name = "nsync"
    homepage = "https://github.com/google/nsync"
    description = "Library that exports various synchronization primitives"
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
            tools.patch(**patch)

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

        if self.settings.os == "Windows" and self.options.shared:
            ar_dest = \
                "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} " \
                "COMPONENT Development"
            rt_dest = 'RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"'
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                f"{ar_dest})", f"{ar_dest}\n{rt_dest})")

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

        self._def_compoment("nsync_c", "nsync")
        self._def_compoment("nsync_cpp")

    def _def_compoment(self, name, lib=None):
        lib = lib if lib else name

        component = self.cpp_info.components[name]
        component.name = name
        component.libs = [lib]
        component.names["cmake_find_package"] = name
        component.names["cmake_find_package_multi"] = name
        component.names["pkg_config"] = lib

        if self.settings.os in ["Linux", "FreeBSD"]:
            component.system_libs = ["pthread"]
