import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


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
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None

    def validate(self):
        if self.settings.compier == "Visual Studio" and self.settings.compiler.version == "14":
            raise ConanInvalidConfiguration("Builds fail for VS 14")  # TODO: add reason in message -> unsupported?

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is None:
            cmake = CMake(self)
            cmake.definitions["WITHOUT_TESTS"] = True
            cmake.configure()
            self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["NonMetricSpaceLib"]
