import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class LibiglConan(ConanFile):
    name = "libigl"
    description = ("Simple C++ geometry processing library")
    topics = ("conan", "libigl", "geometry", "matrices", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libigl.github.io/"
    license = "MPL-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    requires = ("eigen/3.3.9")
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if self.options.shared == True:  
            raise ConanInvalidConfiguration("Recipe is only available as a static lib. Open a PR to add a shared option")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["LIBIGL_EXPORT_TARGETS"] = True
            self._cmake.definitions["LIBIGL_USE_STATIC_LIBRARY"] = True

            # All these dependencies are needed to build the examples or the tests
            self._cmake.definitions["LIBIGL_BUILD_TUTORIALS"] = "OFF"
            self._cmake.definitions["LIBIGL_BUILD_TESTS"] = "OFF"
            self._cmake.definitions["LIBIGL_BUILD_PYTHON"] = "OFF"

            self._cmake.definitions["LIBIGL_WITH_CGAL"] = False
            self._cmake.definitions["LIBIGL_WITH_COMISO"] = False
            self._cmake.definitions["LIBIGL_WITH_CORK"] = False
            self._cmake.definitions["LIBIGL_WITH_EMBREE"] = False
            self._cmake.definitions["LIBIGL_WITH_MATLAB"] = False
            self._cmake.definitions["LIBIGL_WITH_MOSEK"] = False
            self._cmake.definitions["LIBIGL_WITH_OPENGL"] = False
            self._cmake.definitions["LIBIGL_WITH_OPENGL_GLFW"] = False
            self._cmake.definitions["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = False
            self._cmake.definitions["LIBIGL_WITH_PNG"] = False
            self._cmake.definitions["LIBIGL_WITH_TETGEN"] = False
            self._cmake.definitions["LIBIGL_WITH_TRIANGLE"] = False
            self._cmake.definitions["LIBIGL_WITH_XML"] = False
            self._cmake.definitions["LIBIGL_WITH_PYTHON"] = "OFF"
            self._cmake.definitions["LIBIGL_WITH_PREDICATES"] = False
            self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.GPL", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.MPL2", dst="licenses", src=self._source_subfolder)

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "libigl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libigl"
        self.cpp_info.names["cmake_find_package"] = "igl"
        self.cpp_info.names["cmake_find_package_multi"] = "igl"

        self.cpp_info.components["igl_common"].names["cmake_find_package"] = "common"
        self.cpp_info.components["igl_common"].names["cmake_find_package_multi"] = "common"
        self.cpp_info.components["igl_common"].libs = []
        self.cpp_info.components["igl_common"].requires = ["eigen::eigen"]
        if self.settings.os == "Linux":
            self.cpp_info.components["igl_common"].system_libs = ["pthread"]

        self.cpp_info.components["igl_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["igl_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["igl_core"].requires = ["igl_common"]

        self.cpp_info.components["igl_core"].libs = ["igl"]
        self.cpp_info.components["igl_core"].defines = ["IGL_STATIC_LIBRARY"]
