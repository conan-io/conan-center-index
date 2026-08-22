from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

import os

required_conan_version = ">=1.53.0"


class MozjpegConan(ConanFile):
    name = "mozjpeg"
    description = "MozJPEG is an improved JPEG encoder"
    license = ("BSD", "BSD-3-Clause", "ZLIB")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mozilla/mozjpeg"
    topics = ("image", "format", "mozjpeg", "jpg", "jpeg", "picture", "multimedia", "graphics")
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_simd_support:
            del self.options.SIMD

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
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
        if not self._use_cmake:
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.0.3")
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
            tc.variables["CMAKE_SYSTEM_PROCESSOR"] = cmake_system_processor
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["REQUIRE_SIMD"] = bool(self.options.get_safe("SIMD", False))
        tc.variables["WITH_SIMD"] = bool(self.options.get_safe("SIMD", False))
        tc.variables["WITH_ARITH_ENC"] = bool(self.options.arithmetic_encoder)
        tc.variables["WITH_ARITH_DEC"] = bool(self.options.arithmetic_decoder)
        tc.variables["WITH_JPEG7"] = bool(self.options.libjpeg7_compatibility)
        tc.variables["WITH_JPEG8"] = bool(self.options.libjpeg8_compatibility)
        tc.variables["WITH_MEM_SRCDST"] = bool(self.options.mem_src_dst)
        tc.variables["WITH_TURBOJPEG"] = bool(self.options.turbojpeg)
        tc.variables["WITH_JAVA"] = bool(self.options.java)
        tc.variables["WITH_12BIT"] = bool(self.options.enable12bit)
        tc.variables["CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT"] = False
        tc.variables["PNG_SUPPORTED"] = False  # PNG and zlib are only required for executables (and static libraries)
        if is_msvc(self):
            tc.variables["WITH_CRT_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

    def generate_autotools(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
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
        ])
        tc.generate()

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self._use_cmake:
            self.generate_cmake()
        else:
            self.generate_autotools()

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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.package_folder, "lib64"))
        rmdir(self, os.path.join(self.package_folder, "lib64"))
        # remove binaries and pdb files
        for bin_pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            rm(self, pattern=bin_pattern_to_remove, folder=os.path.join(self.package_folder, "bin"))

    def _lib_name(self, name):
        if is_msvc(self) and not self.options.shared:
            return name + "-static"
        return name

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "JPEG")
        self.cpp_info.set_property("cmake_file_name", "mozjpeg")

        cmake_target_suffix = "-static" if not self.options.shared else ""

        # libjpeg
        self.cpp_info.components["libjpeg"].set_property("cmake_module_target_name", "JPEG::JPEG")
        self.cpp_info.components["libjpeg"].set_property("cmake_target_name", f"mozjpeg::jpeg{cmake_target_suffix}")
        self.cpp_info.components["libjpeg"].set_property("pkg_config_name", "libjpeg")
        self.cpp_info.components["libjpeg"].libs = [self._lib_name("jpeg")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libjpeg"].system_libs.append("m")
        # libturbojpeg
        if self.options.turbojpeg:
            self.cpp_info.components["libturbojpeg"].set_property("cmake_target_name", f"mozjpeg::turbojpeg{cmake_target_suffix}")
            self.cpp_info.components["libturbojpeg"].set_property("pkg_config_name", "libturbojpeg")
            self.cpp_info.components["libturbojpeg"].libs = [self._lib_name("turbojpeg")]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libturbojpeg"].system_libs.append("m")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "mozjpeg"
        self.cpp_info.components["libjpeg"].names["cmake_find_package"] = "JPEG"
        self.cpp_info.components["libjpeg"].names["cmake_find_package_multi"] = f"jpeg{cmake_target_suffix}"
        if self.options.turbojpeg:
            self.cpp_info.components["libturbojpeg"].names["cmake_find_package"] = f"turbojpeg{cmake_target_suffix}"
            self.cpp_info.components["libturbojpeg"].names["cmake_find_package_multi"] = f"turbojpeg{cmake_target_suffix}"
