import os
from conans import ConanFile, CMake, tools


class CgalConan(ConanFile):
    name = "cgal"
    license = "LGPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CGAL/cgal"
    description = "C++ library that aims to provide easy access to efficient and reliable algorithms"\
                  "in computational geometry."
    topics = ("geometry", "algorithms")
    settings = "os", "compiler", "build_type", "arch"
    requires = "gmp/6.1.2", "mpfr/4.0.2", "boost/1.71.0", "eigen/3.3.7"

    _source_subfolder = "source_subfolder"

    options = {
        "with_cgal_core": [True, False],
        "with_cgal_qt5": [True, False],
        "with_cgal_imageio": [True, False]
    }

    default_options = {
        "with_cgal_core": True,
        "with_cgal_qt5": False,
        "with_cgal_imageio": False
    }

    generators = "cmake"

    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(CGAL CXX C)", '''project(CGAL CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "cgal-releases-CGAL-{}-branch".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)
        self._patch_sources()

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_CGAL_Core"] = self.options.with_cgal_core
        cmake.definitions["WITH_CGAL_Qt5"] = self.options.with_cgal_qt5
        cmake.definitions["WITH_CGAL_ImageIO"] = self.options.with_cgal_imageio
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        # https://github.com/CGAL/cgal/blob/releases/CGAL-5.0-branch/Installation/lib/cmake/CGAL/CGALConfig.cmake
        for root, _, _ in os.walk(self.source_folder):
            if os.path.isdir(os.path.join(root, "include")) and os.path.isdir(
                    os.path.join(root, "package_info")):
                subdir = os.path.basename(root)
                self.copy("*.h*",
                          dst=os.path.join("include", subdir, "include"),
                          src=os.path.join(root, "include"))
        self.copy("LICENSE*",
                  dst="licenses",
                  src=os.path.join(self._source_subfolder, "Installation"))

    def package_info(self):
        for root, _, _ in os.walk(self.package_folder):
            if os.path.isdir(os.path.join(root, "include")):
                self.cpp_info.includedirs.append(os.path.join(root, "include"))

    def package_id(self):
        self.info.header_only()
