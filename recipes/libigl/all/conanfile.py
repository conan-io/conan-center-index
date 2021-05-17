import os
import stat
import shutil
from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment


class LibiglConan(ConanFile):
    name = "libigl"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                  "(Also Free, Not to Mention Unencumbered by Patents)")
    topics = ("conan", "libigl", "geometry", "matrices", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libigl.github.io/"
    license = "MPL2"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
 
        tools.replace_in_file(self._source_subfolder + "/CMakeLists.txt",
                                  "project(libigl)",
                                  """project(libigl)
# libIGL must find the Eigen3 library imported by conan
# otherwise it downloads a own copy from internet
find_package(Eigen3 REQUIRED) """)

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions["LIBIGL_USE_STATIC_LIBRARY"] = "OFF"
        else:
            cmake.definitions["LIBIGL_USE_STATIC_LIBRARY"] = "ON"

        # All these dependencies are needed to build the examples or the tests
        cmake.definitions["LIBIGL_BUILD_TUTORIALS"] = "OFF"
        cmake.definitions["LIBIGL_BUILD_TESTS"] = "OFF"
        cmake.definitions["LIBIGL_BUILD_PYTHON"] = "OFF"

        cmake.definitions["LIBIGL_WITH_CGAL"] = "OFF"
        cmake.definitions["LIBIGL_WITH_COMISO"] = "OFF"
        cmake.definitions["LIBIGL_WITH_CORK"] = "OFF"
        cmake.definitions["LIBIGL_WITH_EMBREE"] = "OFF"
        cmake.definitions["LIBIGL_WITH_MATLAB"] = "OFF"
        cmake.definitions["LIBIGL_WITH_MOSEK"] = "OFF"
        cmake.definitions["LIBIGL_WITH_OPENGL"] = "OFF"
        cmake.definitions["LIBIGL_WITH_OPENGL_GLFW"] = "OFF"
        cmake.definitions["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = "OFF"
        cmake.definitions["LIBIGL_WITH_PNG"] = "OFF"
        cmake.definitions["LIBIGL_WITH_TETGEN"] = "OFF"
        cmake.definitions["LIBIGL_WITH_TRIANGLE"] = "OFF"
        cmake.definitions["LIBIGL_WITH_XML"] = "OFF"
        cmake.definitions["LIBIGL_WITH_PYTHON"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        self.copy("LICENSE.*", dst="licenses", src=self._source_subfolder)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.cppflags = ["-pthread"]

        if not self.options.shared:
            self.cpp_info.libdirs = ["lib"]
            self.cpp_info.libs = ["libigl.a"]
            self.cpp_info.cppflags += ["-DIGL_STATIC_LIBRARY"]
