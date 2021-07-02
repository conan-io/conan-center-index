from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class RapidcheckConan(ConanFile):
    name = "rapidcheck"
    description = "QuickCheck clone for C++ with the goal of being simple to use with as little boilerplate as possible"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emil-e/rapidcheck"
    license = "BSD-2-Clause"
    topics = "quickcheck", "testing", "property-testing"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_rtti": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported using Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        git_hash = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]
        os.rename("rapidcheck-{}".format(git_hash), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RC_ENABLE_RTTI"] = self.options.enable_rtti
        self._cmake.definitions["RC_ENABLE_TESTS"] = False
        self._cmake.definitions["RC_ENABLE_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["rapidcheck"]
        if self.options.enable_rtti:
            self.cpp_info.defines.append("RC_USE_RTTI")
