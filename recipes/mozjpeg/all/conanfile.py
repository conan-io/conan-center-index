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
        "shared": False,
        "fPIC": True,
        "SIMD": True,
        "arithmetic_encoder": True,
        "arithmetic_decoder": True,
        "libjpeg7_compatibility": False,
        "libjpeg8_compatibility": False,
        "mem_src_dst": True,
        "turbojpeg": True,
        "java": False,
        "enable12bit": False
    }

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        self.provides = ["libjpeg", "libjpeg-turbo"] if self.options.turbojpeg else "libjpeg"

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.3")
        if self.options.SIMD:
            self.build_requires("nasm/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["WITH_SIMD"] = self.options.SIMD
        self._cmake.definitions["WITH_ARITH_ENC"] = self.options.arithmetic_encoder
        self._cmake.definitions["WITH_ARITH_DEC"] = self.options.arithmetic_decoder
        self._cmake.definitions["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        self._cmake.definitions["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        self._cmake.definitions["WITH_MEM_SRCDST"] = self.options.mem_src_dst
        self._cmake.definitions["WITH_TURBOJPEG"] = self.options.turbojpeg
        self._cmake.definitions["WITH_JAVA"] = self.options.java
        self._cmake.definitions["WITH_12BIT"] = self.options.enable12bit
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WITH_CRT_DLL"] = "MD" in str(self.settings.compiler.runtime)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if not self._autotools:
            with tools.chdir(self._source_subfolder):
                self.run("autoreconf -fiv")
            self._autotools = AutoToolsBuildEnvironment(self)
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            args.append("--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic")
            args.append("--with-simd" if self.options.SIMD else "--without-simd")
            args.append("--with-arith-enc" if self.options.arithmetic_encoder else "--without-arith-enc")
            args.append("--with-arith-dec" if self.options.arithmetic_decoder else "--without-arith-dec")
            args.append("--with-jpeg7" if self.options.libjpeg7_compatibility else "--without-jpeg7")
            args.append("--with-jpeg8" if self.options.libjpeg8_compatibility else "--without-jpeg8")
            args.append("--with-mem-srcdst" if self.options.mem_src_dst else "--without-mem-srcdst")
            args.append("--with-turbojpeg" if self.options.turbojpeg else "--without-turbojpeg")
            args.append("--with-java" if self.options.java else "--without-java")
            args.append("--with-12bit" if self.options.enable12bit else "--without-12bit")
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "doc"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)
        # remove binaries and pdb files
        for bin_pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            for bin_file in glob.glob(os.path.join(self.package_folder, "bin", bin_pattern_to_remove)):
                os.remove(bin_file)

    def package_info(self):
        # libjpeg
        self.cpp_info.components["libjpeg"].names["pkg_config"] = "libjpeg"
        self.cpp_info.components["libjpeg"].libs = [self._lib_name("jpeg")]
        if self.settings.os == "Linux":
            self.cpp_info.components["libjpeg"].system_libs.append("m")
        # libturbojpeg
        if self.options.turbojpeg:
            self.cpp_info.components["libturbojpeg"].names["pkg_config"] = "libturbojpeg"
            self.cpp_info.components["libturbojpeg"].libs = [self._lib_name("turbojpeg")]
            if self.settings.os == "Linux":
                self.cpp_info.components["libturbojpeg"].system_libs.append("m")

    def _lib_name(self, name):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and not self.options.shared:
            return name + "-static"
        return name
