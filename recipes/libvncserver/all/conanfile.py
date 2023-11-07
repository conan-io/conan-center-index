from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=1.53.0"


class LibVncServerConan(ConanFile):
    name = "libvncserver"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LibVNC/libvncserver"
    license = "GPL-2.0"
    description = ("A library for easy implementation of a VNC server")
    topics = ("vncserver", "vnc", "rfb")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        #"with_lzo": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
        "with_libpng": [True, False],
        "with_sdl": [True, False],
        "with_gtk": [True, False],
        "with_libssh2": [True, False],
        "with_openssl": [True, False],
        "with_systemd": [True, False],
        #"with_libgcrypt": [True, False],
        "with_ffmpeg": [True, False],
        "with_sasl": [True, False],
        "with_xcb": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        #"with_lzo": False,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_sdl": True,
        "with_gtk": True,
        "with_libssh2": True,
        "with_openssl": True,
        "with_systemd": True,
        #"with_libgcrypt": True,
        "with_ffmpeg": True,
        "with_sasl": True,
        "with_xcb": True,
    }
    
    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Windows"]:
            raise ConanInvalidConfiguration(f"conan is not yet supporting {self.ref} on {self.settings.os}.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_gtk
            del self.options.with_xcb
            del self.options.with_sasl
            del self.options.with_systemd

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        if self.options.get_safe("with_systemd"):
            self.tool_requires("pkgconf/2.0.3")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        #if self.options.with_lzo:
        #    self.requires("lzo/2.10")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        if self.options.with_libpng:
            self.requires("libpng/1.6.40")
        if self.options.with_sdl:
            self.requires("sdl/2.28.2")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        if self.options.with_libssh2:
            self.requires("libssh2/1.11.0")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_systemd"):
            self.requires("libsystemd/253.10")
        #if self.options.with_libgcrypt:
        #    self.requires("libgcrypt/1.8.4")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.0")
        if self.options.get_safe("with_sasl"):
            self.requires("cyrus-sasl/2.1.27")
        if self.options.get_safe("with_xcb"):
            self.requires("xorg/system")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_EXAMPLES"] = False

        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        #tc.variables["WITH_LZO"] = self.options.with_lzo
        tc.variables["WITH_JPEG"] = self.options.with_libjpeg
        tc.variables["WITH_PNG"] = self.options.with_libpng
        tc.variables["WITH_SDL"] = self.options.with_sdl
        tc.variables["WITH_GTK"] = self.options.get_safe("with_gtk")
        tc.variables["WITH_LIBSSH2"] = self.options.with_libssh2
        tc.variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.variables["WITH_SYSTEMD"] = self.options.get_safe("with_systemd")
        #tc.variables["WITH_GCRYPT"] = self.options.with_libgcrypt
        tc.variables["WITH_FFMPEG"] = self.options.with_ffmpeg
        tc.variables["WITH_SASL"] = self.options.get_safe("with_sasl")
        tc.variables["WITH_XCB"] = self.options.get_safe("with_xcb")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibVNCServer")
        self.cpp_info.set_property("cmake_target_name", "libvncserver::libvncserver")
        self.cpp_info.filenames["cmake_find_package"] = "LibVNCServer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "LibVNCServer"
        self.cpp_info.components["server"].set_property("cmake_target_name", "LibVNCServer::vncserver")
        self.cpp_info.components["server"].names["cmake_find_package"] = "vncserver"
        self.cpp_info.components["server"].names["cmake_find_package_multi"] = "vncserver"
        self.cpp_info.components["server"].libs = ['vncserver']
        self.cpp_info.components["server"].system_libs = ['pthread']

        self.cpp_info.components["client"].set_property("cmake_target_name", "LibVNCServer::vncclient")
        self.cpp_info.components["client"].names["cmake_find_package"] = "vncclient"
        self.cpp_info.components["client"].names["cmake_find_package_multi"] = "vncclient"
        self.cpp_info.components["client"].libs = ['vncclient']
        self.cpp_info.components["client"].system_libs = ['pthread']

        self.cpp_info.components["server"].set_property("pkg_config_name", "libvncserver")
        self.cpp_info.components["client"].set_property("pkg_config_name", "libvncclient")

