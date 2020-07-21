from conans import ConanFile, CMake, tools
import os


class LibYAMLConan(ConanFile):
    name = "libyaml"
    version = "0.2.2"
    description = "LibYAML is a YAML parser and emitter library."
    topics = ("conan", "libyaml", "yaml", "parser", "emitter")
    url = "https://github.com/bincrafters/conan-libyaml"
    homepage = "https://github.com/yaml/libyaml"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        sha256 = "46bca77dc8be954686cff21888d6ce10ca4016b360ae1f56962e6882a17aa1fe"
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["YAML_STATIC_LIB_NAME"] = "yaml"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines = ["YAML_DECLARE_EXPORT"] if self.options.shared else ["YAML_DECLARE_STATIC"]
