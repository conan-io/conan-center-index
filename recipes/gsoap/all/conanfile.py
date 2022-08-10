from conan import ConanFile
from conan import tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
import os
import shutil

required_conan_version = ">=1.45.0"

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
        "with_openssl": [True, False],
        "with_ipv6": [True, False],
        "with_cookies": [True, False],
        "with_c_locale": [True, False],
    }
    default_options = {
        'with_openssl': True,
        'with_ipv6': True,
        'with_cookies': True,
        'with_c_locale': True,
    }
    short_paths = True

    def export_sources(self):
        tools.files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        tools.files.copy(self, "*.cmake", os.path.join(self.recipe_folder, "src"), os.path.join(self.export_sources_folder, "src"))
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["GSOAP_PATH"] = "."
        toolchain.variables["BUILD_TOOLS"] = True
        toolchain.variables["WITH_OPENSSL"] = self.options.with_openssl
        toolchain.variables["WITH_IPV6"] = self.options.with_ipv6
        toolchain.variables["WITH_COOKIES"] = self.options.with_cookies
        toolchain.variables["WITH_C_LOCALE"] = self.options.with_c_locale
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def source(self):
        tools.files.get(self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=".")
        cmake.build()

    def build_requirements(self):
        if tools.build.cross_building(self, skip_x64_x86=True) and hasattr(self, 'settings_build'):
            self.tool_requires("gsoap/{}".format(self.version))

        if self.settings.os == "Windows" or (hasattr(self, "settings_build") and self.settings_build.os == "Windows"):
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("bison/3.7.6")
            self.tool_requires("flex/2.6.4")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
            self.requires("zlib/1.2.12")

    def package(self):
        tools.files.copy(self, "GPLv2_license.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        tools.files.copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        shutil.move(os.path.join(self.package_folder, 'import'), os.path.join(self.package_folder, 'bin', 'import'))

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
