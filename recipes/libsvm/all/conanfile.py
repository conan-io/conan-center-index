from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class libsvmConan(ConanFile):
    name = "libsvm"
    description = "Libsvm is a simple, easy-to-use, and efficient software for SVM classification and regression"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.csie.ntu.edu.tw/~cjlin/libsvm/"
    license = "BSD-3-Clause"
    topics = ("conan", "svm", "vector")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
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

    def validate(self):
        if (
            self.settings.compiler == "Visual Studio" and
            "MT" in self.settings.compiler.runtime and
            self.options.shared
        ):
            raise ConanInvalidConfiguration(
                "{} can not be built as shared library + runtime {}.".format(
                    self.name,
                    self.settings.compiler.runtime
                )
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["svm"]
