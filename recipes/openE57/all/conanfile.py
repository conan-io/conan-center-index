from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

class OpenE57Conan(ConanFile):
    name = "opene57"
    description = "A C++ library for reading and writing E57 files, " \
                  "fork of the original libE57 (http://libe57.org)"
    topics = ("conan", "openE57", "e57")
    version = "1.6.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openE57/openE57"
    license = ("MIT", "E57 Software Licenses")
    settings = "os", "compiler", "arch", "build_type"
    options = {"with_examples": [True, False],
               "with_tools": [True, False],
               'with_tests': [True, False],
               "mt": [True, False],
               "shared": [True, False]}
    default_options = {
        'with_examples': False,
        'with_tools': False,
        'with_tests': False,
        'mt': False,
        'shared': False}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.options.shared == True:
            raise ConanInvalidConfiguration("OpenE57 cannot be built as shared library yet")
        
        if self.options.mt == True and self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("The MT compile option is only available for Visual Studio")

    def build_requirements(self):
        if tools.cross_building(self, skip_x64_x86=True) and hasattr(self, 'settings_build'):
            self.build_requires("openE57/{}".format(self.version))

        if self.options.with_tools == True:
            self.build_requires("boost/1.78.0")
            self.options["boost"].multithreading = True
            self.options["boost"].shared = False

    def requirements(self):
        self.requires("icu/70.1")
        self.options["icu"].shared = False

        self.requires("xerces-c/3.2.3")
        self.options["xerces-c"].shared = False

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "openE57-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="LICENSE.libE57", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.defines.append("E57_REFIMPL_REVISION_ID={name}-{version}".format(name=self.name, version=self.version))
        self.cpp_info.defines.append("XERCES_STATIC_LIBRARY")
        self.cpp_info.libs = ["openE57", "openE57las"]

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = self.options.with_examples
        self._cmake.definitions["BUILD_TOOLS"] = self.options.with_tools
        self._cmake.definitions["BUILD_TESTS"] = self.options.with_tests
        self._cmake.definitions["BUILD_WITH_MT"] = self.options.mt
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake
