import glob
import os
from conans import ConanFile, CMake, tools


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer License Version 2.0"
    homepage = "https://github.com/mdadams/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "jasper", "tool-kit", "coding")
    description = "JasPer Image Processing/Coding Tool Kit"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "jpegturbo": [True, False]}
    default_options = {"shared": False, "fPIC": True, "jpegturbo": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.options.jpegturbo:
            self.requires("libjpeg-turbo/2.0.4")
        else:
            self.requires("libjpeg/9d")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-version-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JAS_ENABLE_DOC"] = False
        self._cmake.definitions["JAS_ENABLE_PROGRAMS"] = False
        self._cmake.definitions["JAS_ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        self._cmake.definitions["JAS_ENABLE_OPENGL"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for dll_file in glob.glob(os.path.join(self.package_folder, "bin", "*.dll")):
                if os.path.basename(dll_file).startswith(("concrt", "msvcp", "vcruntime")):
                    os.unlink(dll_file)

    def package_info(self):
        self.cpp_info.libs = ["jasper"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
