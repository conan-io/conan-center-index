import os

from conan import ConanFile, tools
from conans import CMake

class TinyplyConan(ConanFile):
    name = "tinyply"
    description = "C++11 ply 3d mesh format importer & exporter."
    license = ["Unlicense", "BSD-2-Clause"]
    topics = ("conan", "tinyply", "ply", "geometry", "mesh", "file-format")
    homepage = "https://github.com/ddiakopoulos/tinyply"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SHARED_LIB"] = self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _extract_license(self):
        readme = tools.files.load(self, os.path.join(self.source_folder, self._source_subfolder, "readme.md"))
        begin = readme.find("## License")
        return readme[begin:]

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "tinyply"
        self.cpp_info.names["cmake_find_package_multi"] = "tinyply"
        self.cpp_info.names["pkg_config"] = "tinyply"
        self.cpp_info.libs = tools.collect_libs(self)
