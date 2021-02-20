from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class YamlCppConan(ConanFile):
    name = "yaml-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbeder/yaml-cpp"
    topics = ("conan", "yaml", "yaml-parser", "serialization", "data-serialization")
    description = "A YAML parser and emitter in C++"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["YAML_CPP_BUILD_TESTS"] = False
        self._cmake.definitions["YAML_CPP_BUILD_CONTRIB"] = True
        self._cmake.definitions["YAML_CPP_BUILD_TOOLS"] = False
        self._cmake.definitions["YAML_BUILD_SHARED_LIBS"] = self.options.shared

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake files
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'CMake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append('m')
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.defines.append('_NOEXCEPT=noexcept')
