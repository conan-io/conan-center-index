from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class TgbotConan(ConanFile):
    name = "tgbot"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://reo7sp.github.io/tgbot-cpp"
    description = "C++ library for Telegram bot API"
    topics = ("conan", "tgbot", "telegram", "telegram-api", "telegram-bot", "bot")
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    generators = "cmake", "cmake_find_package"
    exports_sources = ['CMakeLists.txt']

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("boost/1.76.0")
        self.requires("libcurl/7.76.0")
        self.requires("openssl/1.1.1k")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # Don't force PIC
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "set_property(TARGET ${PROJECT_NAME} PROPERTY POSITION_INDEPENDENT_CODE ON)",
            ""
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ['TgBot']
