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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
