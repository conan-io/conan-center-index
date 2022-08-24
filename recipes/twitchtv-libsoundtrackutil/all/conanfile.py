from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
from conans.tools import Version
import os

class TwitchTvLibSoundtrackUtilConan(ConanFile):
    name = "twitchtv-libsoundtrackutil"
    license = "MIT"
    homepage = "https://github.com/twitchtv/libsoundtrackutil"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Twitch Soundtrack utility library"
    topics = ("twitch", "soundtrack")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    generators = "cmake"
    exports = ["CMakeLists.txt", "patches/**"]
    requires = ("twitch-native-ipc/3.1.1",
                "ms-gsl/2.0.0",
                )

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_min_version(self):
        return {
            "gcc": "8",
            "clang": "8",
            "apple-clang": "10",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

        min_version = self._compilers_min_version.get(str(self.settings.compiler), False)
        if min_version:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++17".format(self.name))
        else:
            self.output.warn("unknown compiler, assuming C++17 support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format("libsoundtrackutil", self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_CODE_FORMATTING"] = False
        self._cmake.definitions["BUILD_TESTING"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["MSVC_DYNAMIC_RUNTIME"] = self.settings.compiler.runtime in ("MD", "MDd")

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.libs = ["libsoundtrackutil"]

        if tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
