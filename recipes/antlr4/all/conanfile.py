from conans import ConanFile, CMake, tools
import os


class Antlr4Conan(ConanFile):
    name = "antlr4"
    license = "The BSD License"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.antlr.org/"
    topics = ("conan", "antlr", "parsers")
    description = "C++ runtime support for ANTLR"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    requires = "libuuid/1.0.3"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder
        )

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            print("Looking for {}".format(patch))
            tools.patch(**patch)
        cmake = self._configure_cmake()
        if self.options.shared:
            cmake.build(target="antlr4_shared")
        else:
            cmake.build(target="antlr4_static")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["WITH_LIBCXX"] = "OFF"
        cmake.configure(
            build_folder=self._build_subfolder, source_folder=self._source_subfolder
        )
        return cmake

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.h",
            dst="include",
            src=os.path.join(self._source_subfolder, "runtime", "src"),
        )
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.jar", dst="bin", keep_path=False)
        self.copy(
            pattern="*.so*",
            dst="lib",
            src=os.path.join(self._source_subfolder, "dist"),
            keep_path=False,
            symlinks=True,
        )

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
