import os

from conans import ConanFile, CMake, tools

class TinysplineConan(ConanFile):
    name = "tinyspline"
    description = "Library for interpolating, transforming, and querying " \
                  "arbitrary NURBS, B-Splines, and Bezier curves."
    license = "MIT"
    topics = ("conan", "tinyspline ", "nurbs", "b-splines", "bezier")
    homepage = "https://github.com/msteinbeck/tinyspline"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
        "floating_point_precision": ["double", "single"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
        "floating_point_precision": "double"
    }

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
        if not self.options.cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TINYSPLINE_BUILD_DOCS"] = False
        self._cmake.definitions["TINYSPLINE_BUILD_EXAMPLES"] = False
        self._cmake.definitions["TINYSPLINE_BUILD_TESTS"] = False
        self._cmake.definitions["TINYSPLINE_DISABLE_CXX"] = not self.options.cxx
        self._cmake.definitions["TINYSPLINE_DISABLE_CSHARP"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_D"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_GOLANG"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_JAVA"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_LUA"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_OCTAVE"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_PHP"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_PYTHON"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_R"] = True
        self._cmake.definitions["TINYSPLINE_DISABLE_RUBY"] = True
        self._cmake.definitions["TINYSPLINE_FLOAT_PRECISION"] = self.options.floating_point_precision == "single"
        self._cmake.definitions["TINYSPLINE_INSTALL_BINARY_DIR"] = "bin"
        self._cmake.definitions["TINYSPLINE_INSTALL_LIBRARY_DIR"] = "lib"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if tools.Version(self.version) < "0.3.0":
            lib_prefix = "lib" if self.settings.compiler == "Visual Studio" and not self.options.shared else ""
            lib_suffix = "d" if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" else ""
            cpp_prefix = "cpp"
        else:
            lib_prefix = ""
            lib_suffix = ""
            cpp_prefix = "cxx"

        self.cpp_info.components["libtinyspline"].libs = ["{}tinyspline{}".format(lib_prefix, lib_suffix)]
        self.cpp_info.components["libtinyspline"].names["pkg_config"] = "tinyspline"

        # FIXME: create tinysplinecxx::tinysplinecxx in tinycplinecxx-config.cmake
        self.cpp_info.components["libtinysplinecxx"].libs = ["{}tinyspline{}{}".format(lib_prefix, cpp_prefix, lib_suffix)]
        self.cpp_info.components["libtinysplinecxx"].names["pkg_config"] = "tinyspline{}".format(cpp_prefix)

        if self.settings.os == "Linux":
            self.cpp_info.components["libtinyspline"].system_libs = ["m"]
            self.cpp_info.components["libtinysplinecxx"].system_libs = ["m"]
