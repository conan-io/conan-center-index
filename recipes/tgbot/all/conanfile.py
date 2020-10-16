import os
from conans import ConanFile, CMake, tools


class TgbotConan(ConanFile):
    name = "tgbot"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://reo7sp.github.io/tgbot-cpp"
    description = "C++ library for Telegram bot API"
    topics = ("conan", "tgbot", "telegram", "telegram-api", "telegram-bot", "bot")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}

    generators = "cmake", "cmake_find_package"
    exports_sources = ['CMakeLists.txt', 'patches/*']

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.74.0")
        self.requires("libcurl/7.72.0")
        self.requires("openssl/1.1.1h")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ['TgBot']
