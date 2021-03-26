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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = '{}-{}'.format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["INSTALL_CMAKE_DIR"] = 'lib/cmake/libyaml'
        self._cmake.definitions["YAML_STATIC_LIB_NAME"] = "yaml"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # 0.2.2 has LICENSE, 0.2.5 has License, so ignore case
        self.copy(pattern="License", dst="licenses",
                  src=self._source_subfolder, ignore_case=True)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["yaml"].libs = ["yaml"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["yaml"].defines = [
                "YAML_DECLARE_EXPORT" if self.options.shared
                else "YAML_DECLARE_STATIC"
            ]
        self.cpp_info.names["cmake_find_package"] = "yaml"
        self.cpp_info.names["cmake_find_package_multi"] = "yaml"
