from conans import ConanFile, tools, CMake
import os


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    topics = ("conan", "flac", "codec", "audio", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/flac"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", "LPGL-2.1-or-later", "GFDL-1.2")
    requires = "ogg/1.3.4"
    exports_sources = ['CMakeLists.txt', 'patches/*']

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
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'src', 'libFLAC', 'CMakeLists.txt'),
            'target_link_libraries(FLAC PRIVATE $<$<BOOL:${HAVE_LROUND}>:m>)',
            'target_link_libraries(FLAC PUBLIC $<$<BOOL:${HAVE_LROUND}>:m>)')
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            'set(CMAKE_EXE_LINKER_FLAGS -no-pie)',
            '#set(CMAKE_EXE_LINKER_FLAGS -no-pie)')

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
        self.cpp_info.libs = ['FLAC++', 'FLAC']
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs += ["m"]
