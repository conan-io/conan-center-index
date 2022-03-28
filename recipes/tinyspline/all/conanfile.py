from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.36.0"


class TinysplineConan(ConanFile):
    name = "tinyspline"
    description = "Library for interpolating, transforming, and querying " \
                  "arbitrary NURBS, B-Splines, and Bezier curves."
    license = "MIT"
    topics = ("tinyspline ", "nurbs", "b-splines", "bezier")
    homepage = "https://github.com/msteinbeck/tinyspline"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
        "floating_point_precision": ["double", "single"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
        "floating_point_precision": "double",
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TINYSPLINE_BUILD_DOCS"] = False
        cmake.definitions["TINYSPLINE_BUILD_EXAMPLES"] = False
        cmake.definitions["TINYSPLINE_BUILD_TESTS"] = False
        cmake.definitions["TINYSPLINE_DISABLE_CXX"] = not self.options.cxx
        cmake.definitions["TINYSPLINE_DISABLE_CSHARP"] = True
        cmake.definitions["TINYSPLINE_DISABLE_D"] = True
        cmake.definitions["TINYSPLINE_DISABLE_GOLANG"] = True
        cmake.definitions["TINYSPLINE_DISABLE_JAVA"] = True
        cmake.definitions["TINYSPLINE_DISABLE_LUA"] = True
        cmake.definitions["TINYSPLINE_DISABLE_OCTAVE"] = True
        cmake.definitions["TINYSPLINE_DISABLE_PHP"] = True
        cmake.definitions["TINYSPLINE_DISABLE_PYTHON"] = True
        cmake.definitions["TINYSPLINE_DISABLE_R"] = True
        cmake.definitions["TINYSPLINE_DISABLE_RUBY"] = True
        cmake.definitions["TINYSPLINE_FLOAT_PRECISION"] = self.options.floating_point_precision == "single"
        cmake.definitions["TINYSPLINE_INSTALL_BINARY_DIR"] = "bin"
        cmake.definitions["TINYSPLINE_INSTALL_LIBRARY_DIR"] = "lib"
        cmake.configure()
        return cmake

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
            lib_prefix = "lib" if self._is_msvc and not self.options.shared else ""
            lib_suffix = "d" if self._is_msvc and self.settings.build_type == "Debug" else ""
            cpp_prefix = "cpp"
        else:
            lib_prefix = ""
            lib_suffix = ""
            cpp_prefix = "cxx"

        self.cpp_info.set_property("cmake_file_name", "tinyspline")
        self.cpp_info.set_property("cmake_target_name", "tinyspline-do-not-use")
        self.cpp_info.set_property("pkg_config_name", "tinyspline-do-not-use")

        self.cpp_info.components["libtinyspline"].set_property("cmake_target_name", "tinyspline::tinyspline")
        self.cpp_info.components["libtinyspline"].set_property("pkg_config_name", "tinyspline")
        self.cpp_info.components["libtinyspline"].libs = ["{}tinyspline{}".format(lib_prefix, lib_suffix)]

        # FIXME: should live in tinysplinecxx-config.cmake (see https://github.com/conan-io/conan/issues/9000)
        self.cpp_info.components["libtinysplinecxx"].set_property("cmake_target_name", "tinysplinecxx::tinysplinecxx")
        self.cpp_info.components["libtinysplinecxx"].set_property("pkg_config_name", "tinysplinecxx")
        self.cpp_info.components["libtinysplinecxx"].libs = ["{}tinyspline{}{}".format(lib_prefix, cpp_prefix, lib_suffix)]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtinyspline"].system_libs = ["m"]
            self.cpp_info.components["libtinysplinecxx"].system_libs = ["m"]
