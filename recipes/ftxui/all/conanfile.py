import os

import conan.tools.files
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class FTXUIConan(ConanFile):
    name = "ftxui"
    description = "💻 C++ Functional Terminal User Interface."
    license = "MIT"
    topics = ("ncurses", "terminal", "screen", "tui")
    homepage = "https://github.com/ArthurSonzogni/FTXUI"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)
        if compiler == 'gcc' and version < '8':
            raise ConanInvalidConfiguration("gcc 8 required")
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

    def validate(self):
        self._validate_compiler_settings()
        if self.settings.compiler in ["Visual Studio", "msvc"]:
            raise ConanInvalidConfiguration("Visual Studio unsupported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        libs = ['ftxui-dom', 'ftxui-screen', 'ftxui-component']
        ext = '.a'

        for lib in libs:
            src = os.path.join(self.package_folder, "lib", f"{lib}{ext}")
            dst = os.path.join(self.package_folder, "lib", f"lib{lib}{ext}")
            conan.tools.files.rename(self, src, dst)

    def package_info(self):
        self.cpp_info.libs = ['ftxui-dom',
                              'ftxui-screen',
                              'ftxui-component']
