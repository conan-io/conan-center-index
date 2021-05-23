from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class ICCConan(ConanFile):
    name = 'icc'
    homepage = 'https://github.com/redradist/Inter-Component-Communication'
    license = 'MIT'
    url = 'https://github.com/conan-io/conan-center-index'
    description = "I.C.C. - Inter Component Communication, This is a library created to simplify communication between " \
                  "components inside of single application. It is thread safe and could be used for creating " \
                  "components that works in different threads. "
    topics = ("thread-safe", "active object")
    settings = {"os": ["Windows", "Linux"], "compiler": None, "build_type": None, "arch": None}
    options = {
        "shared": [True, False],
        'fPIC': [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    exports_sources = ['CMakeLists.txt', 'patches/*']

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
            "gcc": "4.8.1"
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if tools.Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {}."
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.rename('Inter-Component-Communication-{}'.format(self.version), dst=self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions['ICC_BUILD_SHARED'] = self.options.shared
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.definitions['ICC_BUILD_SHARED'] = self.options.shared
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "icc"
        self.cpp_info.names["cmake_find_multi_package"] = "icc"
        self.cpp_info.libs = ["ICC"]
        self.cpp_info.libdirs = ["bin", "lib"]

        if self.settings.os == 'Android':
            self.cpp_info.system_libs = ['atomic']
