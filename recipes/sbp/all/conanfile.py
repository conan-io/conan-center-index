import os

from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration


class SbpConan(ConanFile):
    name = "sbp"
    license = "MIT"
    homepage = "https://github.com/swift-nav/libsbp"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Swift Binary Protocol client library"
    topics = ("gnss",)
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "c"

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

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now, see issue https://github.com/swift-nav/libsbp/issues/1062")

    def source(self):
        data = self.conan_data["sources"][self.version]

        tools.get(**data["source"], strip_root=True, destination=self._source_subfolder)
        tools.get(**data["cmake"], strip_root=True, destination=os.path.join(self._source_subfolder, "c", "cmake", "common"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["libsbp_ENABLE_TESTS"] = False
        self._cmake.definitions["libsbp_ENABLE_DOCS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(
            "LICENSE",
            src=self._source_subfolder,
            dst="licenses",
            ignore_case=True,
            keep_path=False,
        )
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sbp"]
