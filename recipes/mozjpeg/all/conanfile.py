from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os


required_conan_version = ">=1.33.0"


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
        "enable12bit": False,
    }

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_simd_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_simd_support:
            del self.options.SIMD

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        self.provides = ["libjpeg", "libjpeg-turbo"] if self.options.turbojpeg else "libjpeg"

    @property
    def _use_cmake(self):
        return self.settings.os == "Windows" or tools.Version(self.version) >= "4.0.0"

    def build_requirements(self):
        if not self._use_cmake:
            if self.settings.os != "Windows":
                self.build_requires("libtool/2.4.6")
                self.build_requires("pkgconf/1.7.4")
        if self.options.get_safe("SIMD"):
            self.build_requires("nasm/2.15.05")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.cross_building(self.settings):
            # FIXME: too specific and error prone, should be delegated to CMake helper
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = cmake_system_processor
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["REQUIRE_SIMD"] = self.options.get_safe("SIMD", False)
        self._cmake.definitions["WITH_SIMD"] = self.options.get_safe("SIMD", False)
        self._cmake.definitions["WITH_ARITH_ENC"] = self.options.arithmetic_encoder
        self._cmake.definitions["WITH_ARITH_DEC"] = self.options.arithmetic_decoder
        self._cmake.definitions["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        self._cmake.definitions["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        self._cmake.definitions["WITH_MEM_SRCDST"] = self.options.mem_src_dst
        self._cmake.definitions["WITH_TURBOJPEG"] = self.options.turbojpeg
        self._cmake.definitions["WITH_JAVA"] = self.options.java
        self._cmake.definitions["WITH_12BIT"] = self.options.enable12bit
        self._cmake.definitions["CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT"] = False
        self._cmake.definitions["PNG_SUPPORTED"] = False  # PNG and zlib are only required for executables (and static libraries)
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WITH_CRT_DLL"] = "MD" in str(self.settings.compiler.runtime)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            yes_no = lambda v: "yes" if v else "no"
            args = [
                "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
                "--with-simd={}".format(yes_no(self.options.get_safe("SIMD", False))),
                "--with-arith-enc={}".format(yes_no(self.options.arithmetic_encoder)),
                "--with-arith-dec={}".format(yes_no(self.options.arithmetic_decoder)),
                "--with-jpeg7={}".format(yes_no(self.options.libjpeg7_compatibility)),
                "--with-jpeg8={}".format(yes_no(self.options.libjpeg8_compatibility)),
                "--with-mem-srcdst={}".format(yes_no(self.options.mem_src_dst)),
                "--with-turbojpeg={}".format(yes_no(self.options.turbojpeg)),
                "--with-java={}".format(yes_no(self.options.java)),
                "--with-12bit={}".format(yes_no(self.options.enable12bit)),
                "--enable-shared={}".format(yes_no(self.options.shared)),
                "--enable-static={}".format(yes_no(not self.options.shared)),
            ]
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with tools.files.chdir(self, self._source_subfolder):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        if self._use_cmake:
            cmake = self._configure_cmake()
            cmake.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # remove binaries and pdb files
        for bin_pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), bin_pattern_to_remove)

    def _lib_name(self, name):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and not self.options.shared:
            return name + "-static"
        return name

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
