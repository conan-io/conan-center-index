from conans import ConanFile, tools, CMake
import os


class VorbisConan(ConanFile):
    name = "vorbis"
    version = "1.3.6"
    description = "The VORBIS audio codec library"
    topics = ("conan", "vorbis", "audio", "codec")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "FindVORBIS.cmake"]
    _source_subfolder = "source_subfolder"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    requires = "ogg/1.3.4"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            with tools.chdir(self._source_subfolder):
                tools.replace_in_file('vorbis.pc.in', 'Libs.private: -lm', 'Libs.private:')

    def build(self):
        if self.settings.os == "Linux":
            if 'LDFLAGS' in os.environ:
                os.environ['LDFLAGS'] = os.environ['LDFLAGS'] + ' -lm'
            else:
                os.environ['LDFLAGS'] = '-lm'
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("include/vorbis/*", ".", "%s" % self._source_subfolder, keep_path=True)
        self.copy("%s/copying*" % self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)

        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.pdb", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                elif self.settings.os == "Windows":
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
        for f in ['vorbis', 'vorbisenc', 'vorbisfile']:
            f = os.path.join(self.package_folder, 'bin', '%s.pdb' % f)
            if os.path.isfile(f):
                os.remove(f)

    def package_info(self):
        self.cpp_info.libs = ['vorbisfile', 'vorbisenc', 'vorbis']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.name = 'VORBIS'
        self.cpp_info.names['pkg_config'] = 'vorbis'
