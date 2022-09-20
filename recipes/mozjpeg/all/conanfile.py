from conan import ConanFile
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import cross_building
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.51.3"

class MozjpegConan(ConanFile):
    name = "mozjpeg"
    description = "MozJPEG is an improved JPEG encoder"
    license = ("BSD", "BSD-3-Clause", "ZLIB")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mozilla/mozjpeg"
    topics = ("conan", "image", "format", "mozjpeg", "jpg", "jpeg", "picture", "multimedia", "graphics")
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

    @property
    def _has_simd_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_simd_support:
            del self.options.SIMD

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        self.provides = ["libjpeg", "libjpeg-turbo"] if self.options.turbojpeg else "libjpeg"

    @property
    def _use_cmake(self):
        return self.settings.os == "Windows" or Version(self.version) >= "4.0.0"

    def layout(self):
        if self._use_cmake:
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder='src')

    def build_requirements(self):
        if not self._use_cmake and self.settings.os != "Windows":
            self.tool_requires("libtool/2.4.7")
            self.tool_requires("pkgconf/1.7.4")
        if self.options.get_safe("SIMD"):
            self.tool_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate_cmake(self):
        tc = CMakeToolchain(self)
        if cross_building(self):
            # FIXME: too specific and error prone, should be delegated to CMake helper
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = cmake_system_processor
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["ENABLE_STATIC"] = not bool(self.options.shared)
        tc.cache_variables["ENABLE_SHARED"] = bool(self.options.shared)
        tc.cache_variables["REQUIRE_SIMD"] = bool(self.options.get_safe("SIMD", False))
        tc.cache_variables["WITH_SIMD"] = bool(self.options.get_safe("SIMD", False))
        tc.cache_variables["WITH_ARITH_ENC"] = bool(self.options.arithmetic_encoder)
        tc.cache_variables["WITH_ARITH_DEC"] = bool(self.options.arithmetic_decoder)
        tc.cache_variables["WITH_JPEG7"] = bool(self.options.libjpeg7_compatibility)
        tc.cache_variables["WITH_JPEG8"] = bool(self.options.libjpeg8_compatibility)
        tc.cache_variables["WITH_MEM_SRCDST"] = bool(self.options.mem_src_dst)
        tc.cache_variables["WITH_TURBOJPEG"] = bool(self.options.turbojpeg)
        tc.cache_variables["WITH_JAVA"] = bool(self.options.java)
        tc.cache_variables["WITH_12BIT"] = bool(self.options.enable12bit)
        tc.cache_variables["CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT"] = False
        tc.cache_variables["PNG_SUPPORTED"] = False  # PNG and zlib are only required for executables (and static libraries)
        if is_msvc(self):
            tc.cache_variables["WITH_CRT_DLL"] = is_msvc_static_runtime(self)
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def generate_autotools(self):
        toolchain = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        toolchain.configure_args.append("--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))))
        toolchain.configure_args.append("--with-simd={}".format(yes_no(self.options.get_safe("SIMD", False))))
        toolchain.configure_args.append("--with-arith-enc={}".format(yes_no(self.options.arithmetic_encoder)))
        toolchain.configure_args.append("--with-arith-dec={}".format(yes_no(self.options.arithmetic_decoder)))
        toolchain.configure_args.append("--with-jpeg7={}".format(yes_no(self.options.libjpeg7_compatibility)))
        toolchain.configure_args.append("--with-jpeg8={}".format(yes_no(self.options.libjpeg8_compatibility)))
        toolchain.configure_args.append("--with-mem-srcdst={}".format(yes_no(self.options.mem_src_dst)))
        toolchain.configure_args.append("--with-turbojpeg={}".format(yes_no(self.options.turbojpeg)))
        toolchain.configure_args.append("--with-java={}".format(yes_no(self.options.java)))
        toolchain.configure_args.append("--with-12bit={}".format(yes_no(self.options.enable12bit)))
        toolchain.configure_args.append("--enable-shared={}".format(yes_no(self.options.shared)))
        toolchain.configure_args.append("--enable-static={}".format(yes_no(not self.options.shared)))
        toolchain.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def generate(self):
        if self._use_cmake:
            self.generate_cmake()
        else:
            self.generate_autotools()

        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        if self._use_cmake:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self._use_cmake:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "doc"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, pattern="*.la", folder=os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # remove binaries and pdb files
        for bin_pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            rm(self, pattern=bin_pattern_to_remove, folder=os.path.join(self.package_folder, "bin"))

    def _lib_name(self, name):
        if is_msvc(self) and not self.options.shared:
            return name + "-static"
        return name

    def package_info(self):
        # libjpeg
        self.cpp_info.components["libjpeg"].names["pkg_config"] = "libjpeg"
        self.cpp_info.components["libjpeg"].libs = [self._lib_name("jpeg")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libjpeg"].system_libs.append("m")
        # libturbojpeg
        if self.options.turbojpeg:
            self.cpp_info.components["libturbojpeg"].names["pkg_config"] = "libturbojpeg"
            self.cpp_info.components["libturbojpeg"].libs = [self._lib_name("turbojpeg")]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libturbojpeg"].system_libs.append("m")
