import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from glob import glob


class CppCmdConan(ConanFile):
    name = "cppcmd"
    description = "Simple cpp command interpreter header-only library"
    topics = ("header-only", "interpreter", "cpp")
    homepage = "https://github.com/remysalim/cppcmd"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _supports_cpp17(self):
        supported_compilers = [
            ("gcc", "8"), ("clang", "7"), ("apple-clang", "10.2"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = tools.Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("cppcmd requires C++17 support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob("cppcmd-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder,
                        build_folder=self._build_subfolder)
        cmake.install()

    def package_id(self):
        self.info.header_only()
