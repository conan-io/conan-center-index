import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


class CgalConan(ConanFile):
    name = "cgal"
    license = "GPL-3.0-or-later", "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CGAL/cgal"
    description = "C++ library that aims to provide easy access to efficient and reliable algorithms"\
                  "in computational geometry."
    topics = ("conan", "cgal", "geometry", "algorithms")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    options = {
        "with_cgal_core": [True, False],
        "with_cgal_qt5": [True, False],
        "with_cgal_imageio": [True, False],
        "shared": [True, False],
        "header_only": [True, False]
    }
    default_options = {
        "with_cgal_core": True,
        "with_cgal_qt5": False,
        "with_cgal_imageio": True,
        "shared": False,
        "header_only": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["WITH_CGAL_Core"] = self.options.with_cgal_core
            self._cmake.definitions["WITH_CGAL_Qt5"] = self.options.with_cgal_qt5
            self._cmake.definitions["WITH_CGAL_ImageIO"] = self.options.with_cgal_imageio
            self._cmake.definitions["CGAL_HEADER_ONLY"] = self.options.header_only
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        if tools.Version(self.version) < "5.3":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                "CMAKE_SOURCE_DIR", "CMAKE_CURRENT_SOURCE_DIR")
        else:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                "if(NOT PROJECT_NAME)", "if(TRUE)")

    def configure(self):
        if self.options.with_cgal_qt5:
            raise ConanInvalidConfiguration("Qt Conan package is not available yet.")
        if self.options.header_only:
            del self.options.shared

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")
        self.requires("mpfr/4.1.0")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "CGAL-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.get_safe("shared"):
            for root, _, filenames in os.walk(os.path.join(self.package_folder, "bin")):
                for filename in filenames:
                    if not filename.endswith(".dll"):
                        os.unlink(os.path.join(root, filename))
        else:
            tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        # TODO: add components
        self.cpp_info.names["cmake_find_package"] = "CGAL"
        self.cpp_info.names["cmake_find_package_multi"] = "CGAL"
        if not self.options.header_only:
            self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux" and (self.options.with_cgal_core or self.options.with_cgal_imageio):
            self.cpp_info.system_libs.append("m")
        if not self.options.header_only:
            self.cpp_info.defines.append("CGAL_NOT_HEADER_ONLY=1")
