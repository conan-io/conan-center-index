import os
from conans import ConanFile, CMake, tools


class CgalConan(ConanFile):
    name = "cgal"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CGAL/cgal"
    description = "C++ library that aims to provide easy access to efficient and reliable algorithms"\
                  "in computational geometry."
    topics = ("geometry", "algorithms")
    settings = "os", "compiler", "build_type", "arch"
    requires = "mpir/3.0.0", "mpfr/4.0.2", "boost/1.71.0", "eigen/3.3.7"
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _cmake = None

    options = {
        "with_cgal_core": [True, False],
        "with_cgal_qt5": [True, False],
        "with_cgal_imageio": [True, False]
    }

    default_options = {
        "with_cgal_core": True,
        "with_cgal_qt5": False,
        "with_cgal_imageio": True
    }

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["WITH_CGAL_Core"] = self.options.with_cgal_core
            self._cmake.definitions["WITH_CGAL_Qt5"] = self.options.with_cgal_qt5
            self._cmake.definitions["WITH_CGAL_ImageIO"] = self.options.with_cgal_imageio
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(CGAL CXX C)", '''project(CGAL CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "CGAL-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)
        self._patch_sources()

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=os.path.join(self._source_subfolder))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CGAL"
        self.cpp_info.names["cmake_find_package_multi"] = "CGAL"

    def package_id(self):
        self.info.header_only()
