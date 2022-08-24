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

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_lcms": [True, False],
        "with_jasper": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "with_lcms": True,
        "with_jasper": True
    }

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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        # TODO: RawSpeed dependency (-DUSE_RAWSPEED)
        # TODO: DNG SDK dependency (-DUSE_DNGSDK)
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.1")
        if self.options.with_lcms:
            self.requires("lcms/2.12")
        if self.options.with_jasper:
            self.requires("jasper/2.0.33")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
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
