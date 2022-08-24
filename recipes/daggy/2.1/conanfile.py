from conan import ConanFile, tools
from conans import CMake, errors
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class DaggyConan(ConanFile):
    name = "daggy"
    license = "MIT"
    homepage = "https://daggy.dev"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Data Aggregation Utility and C/C++ developer library for data streams catching"
    topics = ("streaming", "qt", "monitoring", "process", "stream-processing", "extensible", "serverless-framework", "aggregation", "ssh2", "crossplatform", "ssh-client")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_ssh2": [True, False],
        "with_yaml": [True, False],
        "with_console": [True, False],
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "with_ssh2": True,
        "with_yaml": True,
        "with_console": False,
        "shared": False,
        "fPIC": True
    }
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        self.build_requires("cmake/3.21.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        self.options["qt"].shared = True
    
    def configure(self):
          if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, 
                    self._minimum_cpp_standard, 
                    self.settings.compiler, 
                    self.settings.compiler.version))

        if not self.options["qt"].shared: 
            raise ConanInvalidConfiguration("Shared Qt lib is required.") 

    def requirements(self):
        self.requires("qt/6.2.2")
        self.requires("kainjow-mustache/4.1")

        if self.options.with_yaml:
            self.requires("yaml-cpp/0.7.0")

        if self.options.with_ssh2:
            self.requires("libssh2/1.10.0")

    def _configure(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SSH2_SUPPORT"] = self.options.with_ssh2
        self._cmake.definitions["YAML_SUPPORT"] = self.options.with_yaml
        self._cmake.definitions["CONSOLE"] = self.options.with_console
        self._cmake.definitions["PACKAGE_DEPS"] = False
        self._cmake.definitions["VERSION"] = self.version
        self._cmake.definitions["CONAN_BUILD"] = True
        self._cmake.definitions["BUILD_TESTING"] = False

        if self.options.shared:
            self._cmake.definitions["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            self._cmake.definitions["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            self._cmake.definitions["CMAKE_VISIBILITY_INLINES_HIDDEN"] = 1
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        
        cmake = self._configure()
        cmake.build()

    def package(self):
        cmake = self._configure()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["DaggyCore"]


        
