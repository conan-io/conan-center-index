from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.43.0"


class UncrustifyConan(ConanFile):
    name = "uncrustify"
    description = "Code beautifier"
    license = "GPL2"
    topics = ("beautifier", "command-line")
    homepage = "https://github.com/uncrustify/uncrustify"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("oatpp-sqlite requires GCC >=8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        if self.settings.os == "Windows":
            shutil.move(os.path.join(self.package_folder, "uncrustify.exe"),
                    os.path.join(self.package_folder, "bin", "uncrustify.exe"))
            os.remove(os.path.join(self.package_folder, "AUTHORS"))
            os.remove(os.path.join(self.package_folder, "BUGS"))
            os.remove(os.path.join(self.package_folder, "ChangeLog"))
            os.remove(os.path.join(self.package_folder, "HELP"))
            os.remove(os.path.join(self.package_folder, "README.md"))
            tools.rmdir(os.path.join(self.package_folder, "cfg"))

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
        tools.rmdir(os.path.join(self.package_folder, "share"))
