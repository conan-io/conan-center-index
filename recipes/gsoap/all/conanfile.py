from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.46.0"


class GsoapConan(ConanFile):
    name = "gsoap"
    description = "The gSOAP toolkit is a C and C++ software development toolkit for SOAP and " \
                  "REST XML Web services and generic C/C++ XML data bindings."
    license = ("gSOAP-1.3b", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/gsoap2"
    topics = ("gsoap", "logging")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_ipv6": [True, False],
        "with_cookies": [True, False],
        "with_c_locale": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_ipv6": True,
        "with_cookies": True,
        "with_c_locale": True,
    }

    exports_sources = "CMakeLists.txt", "cmake/*.cmake"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
            self.requires("zlib/1.2.12")

    def build_requirements(self):
        if cross_building(self, skip_x64_x86=True) and hasattr(self, "settings_build"):
            self.tool_requires("gsoap/{}".format(self.version))

        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("bison/3.7.6")
            self.tool_requires("flex/2.6.4")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["GSOAP_PATH"] = self.source_folder.replace("\\", "/")
        toolchain.variables["BUILD_TOOLS"] = True
        toolchain.variables["WITH_OPENSSL"] = self.options.with_openssl
        toolchain.variables["WITH_IPV6"] = self.options.with_ipv6
        toolchain.variables["WITH_COOKIES"] = self.options.with_cookies
        toolchain.variables["WITH_C_LOCALE"] = self.options.with_c_locale
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

        ms = VirtualBuildEnv(self)
        ms.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "GPLv2_license.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        defines = []
        if self.options.with_openssl:
            libs = ["gsoapssl++", ]
            defines.append("WITH_OPENSSL")
            defines.append("WITH_GZIP")
        else:
            libs = ["gsoap++", ]
        self.cpp_info.libs = libs

        if self.options.with_ipv6:
            defines.append("WITH_IPV6")
        if self.options.with_cookies:
            defines.append("WITH_COOKIES")
        if self.options.with_c_locale:
            defines.append("WITH_C_LOCALE")
        self.cpp_info.defines = defines

        # TODO: remove this block if required_conan_version changed to 1.51.1 or higher
        #       (see https://github.com/conan-io/conan/pull/11790)
        self.cpp_info.requires = ["openssl::openssl", "zlib::zlib"]
