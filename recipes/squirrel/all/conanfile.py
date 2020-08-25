import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class SquirrelConan(ConanFile):
    name = "squirrel"
    description = "Squirrel is a high level imperative, object-oriented programming language, designed to be a light-weight scripting language that fits in the size, memory bandwidth, and real-time requirements of applications like video games."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.squirrel-lang.org/"
    license = "MIT"
    topics = ("conan", "fruit", "injection")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        if tools.Version(self.version) <= "3.1":
            if self.settings.os == "Macos":
                raise ConanInvalidConfiguration("squirrel 3.1 and earlier does not support Macos")
            if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "9":
                raise ConanInvalidConfiguration("squirrel 3.1 and earlier does not support Clang 8 and earlier")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var : {}".format(binpath))
        self.env_info.PATH.append(binpath)
