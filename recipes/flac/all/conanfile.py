from conans import ConanFile, tools, CMake
import os


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    topics = ("conan", "flac", "codec", "audio", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/flac"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", "LPGL-2.1-or-later", "GFDL-1.2")
    exports_sources = ["CMakeLists.txt", "patches/*"]

    generators = "cmake",
    settings = "os", "compiler", "build_type", "arch"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("ogg/1.3.4")

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share"), src=os.path.join(self._source_subfolder, "include", "share"), keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share", "grabbag"),
                  src=os.path.join(self._source_subfolder, "include", "share", "grabbag"), keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "flac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "flac"
        self.cpp_info.names["cmake_find_package"] = "FLAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FLAC"

        self.cpp_info.components["libflac"].libs = ["FLAC"]
        self.cpp_info.components["libflac"].names["cmake_find_package"] = "FLAC"
        self.cpp_info.components["libflac"].names["cmake_find_package_multi"] = "FLAC"
        self.cpp_info.components["libflac"].names["pkg_config"] = "flac"
        self.cpp_info.components["libflac"].requires = ["ogg::ogg"]

        self.cpp_info.components["libflac++"].libs = ["FLAC++"]
        self.cpp_info.components["libflac++"].requires = ["libflac"]
        self.cpp_info.components["libflac++"].names["cmake_find_package"] = "FLAC++"
        self.cpp_info.components["libflac++"].names["cmake_find_package_multi"] = "FLAC++"
        self.cpp_info.components["libflac++"].names["pkg_config"] = "flac++"
        if not self.options.shared:
            self.cpp_info.components["libflac"].defines = ["FLAC__NO_DLL"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libflac"].system_libs += ["m"]
