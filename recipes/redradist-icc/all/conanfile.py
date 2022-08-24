from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration, ConanException
import os


class ICCConan(ConanFile):
    name = 'redradist-icc'
    homepage = 'https://github.com/redradist/Inter-Component-Communication'
    license = 'MIT'
    url = 'https://github.com/conan-io/conan-center-index'
    description = "I.C.C. - Inter Component Communication, This is a library created to simplify communication between " \
                  "components inside of single application. It is thread safe and could be used for creating " \
                  "components that works in different threads. "
    topics = ("thread-safe", "active-object", "communication")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "apple-clang": "9.4",
            "clang": "3.3",
            "gcc": "4.9.4"
        }

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions['ICC_BUILD_SHARED'] = self.options.shared
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        os = self.settings.os
        if os not in ("Windows", "Linux"):
            msg = (
                "OS {} is not supported !!"
            ).format(os)
            raise ConanInvalidConfiguration(msg)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {} !!"
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "icc"
        self.cpp_info.names["cmake_find_package_multi"] = "icc"
        if self.options.shared:
            self.cpp_info.libs = ["ICC"]
        else:
            self.cpp_info.libs = ["ICC_static"]

        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ['ws2_32', 'wsock32']
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs = ['pthread']
