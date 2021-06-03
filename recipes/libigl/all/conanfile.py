import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class LibiglConan(ConanFile):
    name = "libigl"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                  "(Also Free, Not to Mention Unencumbered by Patents)")
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            
        if self.settings.os == "Macos" and self.options.shared: # Move to validate
            raise ConanInvalidConfiguration("MacOS shared is currently unsupported please open a PR")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
 

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LIBIGL_USE_STATIC_LIBRARY"] = not self.options.shared
        cmake.definitions["LIBIGL_EXPORT_TARGETS"] = True

        # All these dependencies are needed to build the examples or the tests
        cmake.definitions["LIBIGL_BUILD_TUTORIALS"] = "OFF"
        cmake.definitions["LIBIGL_BUILD_TESTS"] = "OFF"
        cmake.definitions["LIBIGL_BUILD_PYTHON"] = "OFF"

        cmake.definitions["LIBIGL_WITH_CGAL"] = False
        cmake.definitions["LIBIGL_WITH_COMISO"] = False
        cmake.definitions["LIBIGL_WITH_CORK"] = False
        cmake.definitions["LIBIGL_WITH_EMBREE"] = False
        cmake.definitions["LIBIGL_WITH_MATLAB"] = False
        cmake.definitions["LIBIGL_WITH_MOSEK"] = False
        cmake.definitions["LIBIGL_WITH_OPENGL"] = False
        cmake.definitions["LIBIGL_WITH_OPENGL_GLFW"] = False
        cmake.definitions["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = False
        cmake.definitions["LIBIGL_WITH_PNG"] = False
        cmake.definitions["LIBIGL_WITH_TETGEN"] = False
        cmake.definitions["LIBIGL_WITH_TRIANGLE"] = False
        cmake.definitions["LIBIGL_WITH_XML"] = False
        cmake.definitions["LIBIGL_WITH_PYTHON"] = "OFF"
        cmake.definitions["LIBIGL_WITH_PREDICATES"] = False
        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.GPL", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.MPL2", dst="licenses", src=self._source_subfolder)

        self.copy(pattern="*.h", src=self._source_subfolder)
        self.copy(pattern="*.cpp", src=self._source_subfolder)

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "tutorial"))
        tools.rmdir(os.path.join(self.package_folder, "tests"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)

    def package_info(self):
        # FIXME: CMake targets are not installed under a namespace https://github.com/libigl/libigl/blob/36e8435a2f724e83e14f79d128102d06b514a4f4/cmake/libigl.cmake#L543
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

        if not self.options.shared:
            self.cpp_info.defines = ["IGL_STATIC_LIBRARY"]
