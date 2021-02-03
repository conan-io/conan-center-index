import os

from conans import ConanFile, CMake, tools

class LibgeotiffConan(ConanFile):
    name = "libgeotiff"
    description = "Libgeotiff is an open source library normally hosted on top " \
                  "of libtiff for reading, and writing GeoTIFF information tags."
    license = ["MIT", "BSD-3-Clause"]
    topics = ("conan", "libgeotiff", "geotiff", "tiff")
    homepage = "https://github.com/OSGeo/libgeotiff"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("libtiff/4.2.0")
        self.requires("proj/7.2.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_UTILITIES"] = False
        self._cmake.definitions["WITH_TOWGS84"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "libgeotiff"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file),
            {
                "geotiff_library": "GeoTIFF::GeoTIFF",
                "geotiff_library": "geotiff::geotiff"
            }
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += (
                "if(TARGET {aliased} AND NOT TARGET {alias})\n"
                "    add_library({alias} INTERFACE IMPORTED)\n"
                "    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})\n"
                "endif()\n"
            ).format(alias=alias, aliased=aliased)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GeoTIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "geotiff"
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.build_modules = [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
