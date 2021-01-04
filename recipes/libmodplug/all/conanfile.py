from conans import ConanFile, CMake, tools
import os


class LibmodplugConan(ConanFile):
    name = "libmodplug"
    description = "libmodplug - the library which was part of the Modplug-xmms project"
    topics = ("conan", "libmodplug", "auduo", "multimedia", "sound", "music", "mod", "mod music",
              "tracket music")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://modplug-xmms.sourceforge.net"
    license = "Unlicense"  # public domain
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        commit = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + commit
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["modplug"]
        self.cpp_info.bindirs = ["lib"]
        self.cpp_info.includedirs.append(os.path.join("include", "libmodplug"))
        if not self.options.shared:
            self.cpp_info.defines.append("MODPLUG_STATIC")
