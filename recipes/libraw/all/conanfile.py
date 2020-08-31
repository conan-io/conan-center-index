from conans import ConanFile, tools, CMake
import glob
import os


class LibRawConan(ConanFile):
    name = "libraw"
    description = "LibRaw is a library for reading RAW files obtained from digital photo cameras (CRW/CR2, NEF, RAF, DNG, and others)."
    topics = ["image", "photography", "raw"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libraw.org/"
    license = "CDDL-1.0/LGPL-2.1-only"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "rawspeed": [True, False],
        "with_libjpeg": [False, "libjpeg-turbo", "libjpeg"],
        "with_zlib": [True, False],
        "with_lcms": [True, False],
        "with_jasper": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "rawspeed": False,
        "with_libjpeg": "libjpeg-turbo",
        "with_zlib": True,
        "with_lcms": True,
        "with_jasper": True,
        "with_openmp": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _cmake_subfolder(self):
        return "cmake_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_lcms:
            self.requires("lcms/2.11")
        if self.options.rawspeed:
            self.requires("libxml2/2.9.10")
        if self.options.with_jasper:
            self.requires("jasper/2.0.19")

    def source(self):
        for src in self.conan_data["sources"][self.version]:
            tools.get(**src)
        os.rename("LibRaw-{}".format(self.version), self._source_subfolder)
        os.rename(glob.glob("LibRaw-cmake-*")[0], self._cmake_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_JASPER"] = self.options.with_jasper
        self._cmake.definitions["ENABLE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["ENABLE_JPEG"] = self.options.with_libjpeg != False
        self._cmake.definitions["ENABLE_OPENMP"] = self.options.with_openmp

        self._cmake.definitions["ENABLE_EXAMPLES"] = False

        self._cmake.definitions["LIBRAW_PATH"] = os.path.join(self.source_folder, self._source_subfolder)
        self._cmake.definitions["LIBRAW_INSTALL"] = True
        self._cmake.definitions["INSTALL_CMAKE_MODULE_PATH"] = os.path.join(self.package_folder, "lib", "cmake")

        self._cmake.verbose = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))


    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "LibRaw"
        self.cpp_info.filenames["cmake_find_package_multi"] = "LibRaw"

        self.cpp_info.components["raw"].libs = ["raw"]
        self.cpp_info.components["raw_r"].libs = ["raw_r"]

        if self.settings.os == "Linux":
            self.cpp_info.components["raw_r"].system_libs = ["pthread"]

        if self.options.with_openmp:
            self.cpp_info.components["raw"].sharedlinkflags = ["-fopenmp"]
            self.cpp_info.components["raw_r"].sharedlinkflags = ["-fopenmp"]
            self.cpp_info.components["raw"].exelinkflags = ["-fopenmp"]
            self.cpp_info.components["raw_r"].exelinkflags = ["-fopenmp"]

        if self.settings.os == "Windows":
            self.cpp_info.components["raw"].defines.append("WIN32")
            self.cpp_info.components["raw_r"].defines.append("WIN32")

        if not self.options.shared:
            self.cpp_info.components["raw"].defines.append("LIBRAW_NODLL")
            self.cpp_info.components["raw_r"].defines.append("LIBRAW_NODLL")

        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.components["raw"].requires.append("libjpeg::libjpeg")
            self.cpp_info.components["raw_r"].requires.append("libjpeg::libjpeg")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.components["raw"].requires.append("libjpeg-turbo::libjpeg-turbo")
            self.cpp_info.components["raw_r"].requires.append("libjpeg-turbo::libjpeg-turbo")
        if self.options.with_zlib:
            self.cpp_info.components["raw"].requires.append("zlib::zlib")
            self.cpp_info.components["raw_r"].requires.append("zlib::zlib")
        if self.options.with_lcms:
            self.cpp_info.components["raw"].requires.append("lcms::lcms")
            self.cpp_info.components["raw_r"].requires.append("lcms::lcms")
        if self.options.rawspeed:
            self.cpp_info.components["raw"].requires.append("libxml2::libxml2")
            self.cpp_info.components["raw_r"].requires.append("libxml2::libxml2")
        if self.options.with_jasper:
            self.cpp_info.components["raw"].requires.append("jasper::jasper")
            self.cpp_info.components["raw_r"].requires.append("jasper::jasper")
