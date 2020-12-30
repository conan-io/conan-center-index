from conans import ConanFile, CMake, tools
import os
import glob


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    url = "https://github.com/conan-io/conan-center-index"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    topics = ("conan", "jpeg2000", "jp2", "openjpeg", "image", "multimedia", "format", "graphics")
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD 2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_codec": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_codec": False
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.options.build_codec # not used for the moment

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        self._cmake.definitions["BUILD_DOC"] = False
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_LUTS_GENERATOR"] = False
        self._cmake.definitions["BUILD_CODEC"] = False
        self._cmake.definitions["BUILD_MJ2"] = False
        self._cmake.definitions["BUILD_JPWL"] = False
        self._cmake.definitions["BUILD_JPIP"] = False
        self._cmake.definitions["BUILD_VIEWER"] = False
        self._cmake.definitions["BUILD_JAVA"] = False
        self._cmake.definitions["BUILD_JP3D"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_PKGCONFIG_FILES"] = False
        self._cmake.definitions["OPJ_DISABLE_TPSOT_FIX"] = False
        self._cmake.definitions["OPJ_USE_THREAD"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", self._openjpeg_subdir))

    @property
    def _openjpeg_subdir(self):
        openjpeg_version = tools.Version(self.version)
        return "openjpeg-{}.{}".format(openjpeg_version.major, openjpeg_version.minor)

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", self._openjpeg_subdir))
        self.cpp_info.libs = ["openjp2"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("OPJ_STATIC")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["m"]
        # FIXME: CMake imported target should be openjp2
        self.cpp_info.names["cmake_find_package"] = "OpenJPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenJPEG"
        self.cpp_info.names["pkg_config"] = "libopenjp2"
