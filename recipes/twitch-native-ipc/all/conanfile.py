from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import glob


class TwitchNativeIpcConan(ConanFile):
    name = "twitch-native-ipc"
    license = "MIT"
    homepage = "https://github.com/twitchtv/twitch-native-ipc"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Twitch natve ipc library"
    topics = ("twitch", "ipc")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports = ["CMakeLists.txt", "patches/**"]
    requires = "libuv/1.38.1"

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
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version.value) < "15":
                raise ConanInvalidConfiguration("MSVC < 14 unsupported")
        elif self.settings.os == "Macos":
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version.value) < "10":
                raise ConanInvalidConfiguration("apple-clang < 10 unsupported")
        else:
            raise ConanInvalidConfiguration("Only Windows and Macos supported")

        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_CODE_FORMATTING"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        if self.settings.os == "Windows":
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

        pdb_files = glob.glob(os.path.join(self.package_folder, "lib", "*.pdb"), recursive=True)
        for pdb in pdb_files:
            os.unlink(pdb)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["NATIVEIPC_IMPORT"]
