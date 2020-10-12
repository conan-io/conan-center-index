from conans import ConanFile, CMake, tools
import os


class TwitchNativeIpcConan(ConanFile):
    name = "twitch-native-ipc"
    license = "MIT"
    homepage = "https://github.com/twitchtv/twitch-native-ipc"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Twitch natve ipc library"
    topics = ("<twitch>", "<ipc>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True, "libuv:shared": False}
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
        if self.settings.os_build != "Windows" and self.settings.os_build != "Macos":
            raise ConannvalidConfiguration("Only Windows and Macos supported")

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
            self._cmake.definitions["MSVC_DYNAMIC_RUNTIME"] = False if self.settings.compiler.runtime in ["MT", "MTd"] else True

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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
