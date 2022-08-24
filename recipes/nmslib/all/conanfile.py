import os
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration


class Nmslib(ConanFile):
    name = "nmslib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nmslib/nmslib"
    description = "Non-Metric Space Library (NMSLIB): An efficient similarity search library and a toolkit for evaluation of k-NN methods for generic non-metric spaces."
    topics = ("knn-search", "non-metric", "neighborhood-graphs", "neighborhood-graphs", "vp-tree")
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

    _cmake = None

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == "14":
                raise ConanInvalidConfiguration("Visual Studio 14 builds are not supported")  # TODO: add reason in message
            if self.options.shared:
                raise ConanInvalidConfiguration("Visual Studio shared builds are not supported (.lib artifacts missing)")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is None:
            cmake = CMake(self)
            cmake.definitions["WITHOUT_TESTS"] = True
            cmake.configure()
            self._cmake = cmake
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["NonMetricSpaceLib"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
