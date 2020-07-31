from conans import ConanFile, tools, CMake
import os

class LibRawConan(ConanFile):
    name = "libraw"
    description = "LibRaw is a library for reading RAW files obtained from digital photo cameras (CRW/CR2, NEF, RAF, DNG, and others)."
    topics = ["image", "photography", "raw"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libraw.org/"
    license = "CDDL-1.0/LGPL-2.1-only"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("libjpeg/9d")
        self.requires("lcms/2.11")
        self.requires("jasper/2.0.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("LibRaw-" + self.version, self._source_subfolder)

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
        cmake = self._configure_cmake()
        cmake.install()
        
        self.copy("LICENSE.*", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("WIN32")

        if not self.options.shared:
            self.cpp_info.defines.append("LIBRAW_NODLL")
