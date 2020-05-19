from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os
import glob


class MozjpegConan(ConanFile):
    name = "mozjpeg"
    description = "MozJPEG is an improved JPEG encoder"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "image", "format", "mozjpeg", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = ("BSD", "BSD-3-Clause", "ZLIB")
    homepage = "https://github.com/mozilla/mozjpeg"
    exports_sources = ("CMakeLists.txt", "patches/*")
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "SIMD": [True, False],
        "arithmetic_encoder": [True, False],
        "arithmetic_decoder": [True, False],
        "libjpeg7_compatibility": [True, False],
        "libjpeg8_compatibility": [True, False],
        "mem_src_dst": [True, False],
        "turbojpeg": [True, False],
        "java": [True, False],
        "enable12bit": [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'SIMD': True,
        'arithmetic_encoder': True,
        'arithmetic_decoder': True,
        'libjpeg7_compatibility': False,
        'libjpeg8_compatibility': False,
        'mem_src_dst': True,
        'turbojpeg': True,
        'java': False,
        'enable12bit': False
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("nasm/2.13.02")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_TESTING'] = False
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['WITH_SIMD'] = self.options.SIMD
        cmake.definitions['WITH_ARITH_ENC'] = self.options.arithmetic_encoder
        cmake.definitions['WITH_ARITH_DEC'] = self.options.arithmetic_decoder
        cmake.definitions['WITH_JPEG7'] = self.options.libjpeg7_compatibility
        cmake.definitions['WITH_JPEG8'] = self.options.libjpeg8_compatibility
        cmake.definitions['WITH_MEM_SRCDST'] = self.options.mem_src_dst
        cmake.definitions['WITH_TURBOJPEG'] = self.options.turbojpeg
        cmake.definitions['WITH_JAVA'] = self.options.java
        cmake.definitions['WITH_12BIT'] = self.options.enable12bit
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions['WITH_CRT_DLL'] = 'MD' in str(self.settings.compiler.runtime)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _configure_autotools(self):
        if not self._autotools:
            with tools.chdir(self._source_subfolder):
                self.run('autoreconf -fiv')
            self._autotools = AutoToolsBuildEnvironment(self)
            args = []
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            args.append('--with-pic' if self.options.fPIC else '--without-pic')
            args.append('--with-simd' if self.options.SIMD else '--without-simd')
            args.append('--with-arith-enc' if self.options.arithmetic_encoder else '--without-arith-enc')
            args.append('--with-arith-dec' if self.options.arithmetic_decoder else '--without-arith-dec')
            args.append('--with-jpeg7' if self.options.libjpeg7_compatibility else '--without-jpeg7')
            args.append('--with-jpeg8' if self.options.libjpeg8_compatibility else '--without-jpeg8')
            args.append('--with-mem-srcdst' if self.options.mem_src_dst else '--without-mem-srcdst')
            args.append('--with-turbojpeg' if self.options.turbojpeg else '--without-turbojpeg')
            args.append('--with-java' if self.options.java else '--without-java')
            args.append('--with-12bit' if self.options.enable12bit else '--without-12bit')
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == 'Windows':
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        if self.settings.os == 'Windows':
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

        # remove binaries
        for bin_program in ['cjpeg', 'djpeg', 'jpegtran', 'tjbench', 'wrjpgcom', 'rdjpgcom']:
            for ext in ['', '.exe']:
                try:
                    os.remove(os.path.join(self.package_folder, 'bin', bin_program+ext))
                except OSError:
                    pass
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

        # drop la files
        for la in ['libjpeg', 'libturbojpeg']:
            la_file = os.path.join(self.package_folder, "lib", la + ".la")
            if os.path.isfile(la_file):
                os.unlink(la_file)

        tools.rmdir(os.path.join(self.package_folder, 'doc'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
