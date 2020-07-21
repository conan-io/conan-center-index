from conans import ConanFile, CMake, tools
import os


class LibYAMLConan(ConanFile):
    name = "libyaml"
    description = "LibYAML is a YAML parser and emitter library."
    topics = ("conan", "libyaml", "yaml", "parser", "emitter")
    url = "https://github.com/conan-io/conan-center-index"
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
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = '{}-{}'.format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["INSTALL_CMAKE_DIR"] = 'lib/cmake/libyaml'
        cmake.definitions["YAML_STATIC_LIB_NAME"] = "yaml"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # 0.2.2 has LICENSE, 0.2.5 has License, so ignore case
        self.copy(pattern="License", dst="licenses",
                  src=self._source_subfolder, ignore_case=True)
        cmake = self._configure_cmake()
        cmake.install()
        os.unlink(os.path.join(self.package_folder, "lib", "cmake", "libyaml",
                               "yamlConfig.cmake"))
        os.unlink(os.path.join(self.package_folder, "lib", "cmake", "libyaml",
                               "yamlConfigVersion.cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines = (["YAML_DECLARE_EXPORT"] if
                                     self.options.shared else
                                     ["YAML_DECLARE_STATIC"])
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
