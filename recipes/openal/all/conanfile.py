from conans import CMake, ConanFile, tools
import os


class OpenALConan(ConanFile):
    name = "openal"
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    topics = ("conan", "openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openal.org"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.1.9")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "openal-soft-openal-soft-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['LIBTYPE'] = 'SHARED' if self.options.shared else 'STATIC'
        cmake.definitions['ALSOFT_UTILS'] = False
        cmake.definitions['ALSOFT_EXAMPLES'] = False
        cmake.definitions['ALSOFT_TESTS'] = False
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_SoundIO'] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.extend(['dl', 'm'])
        elif self.settings.os == 'Macos':
            self.cpp_info.frameworks.extend(['AudioToolbox', 'CoreAudio', 'CoreFoundation'])
        elif self.settings.os == 'Windows':
            self.cpp_info.system_libs.extend(['winmm', 'ole32', 'shell32'])
        self.cpp_info.includedirs = ["include", "include/AL"]
        if not self.options.shared:
            self.cpp_info.defines.append('AL_LIBTYPE_STATIC')
