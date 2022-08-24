import os

from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LibcapConan(ConanFile):
    name = "libcap"
    license = ("GPL-2.0-only", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libcap/libcap.git"
    description = "This is a library for getting and setting POSIX.1e" \
                  " (formerly POSIX 6) draft 15 capabilities"
    topics = ("conan", "libcap", "capabilities")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "psx_syscals": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "psx_syscals": False,
    }
    exports_sources = "patches/**"

    _autotools = None
    _autotools_env = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools, self._autotools_env
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.fpic = self.options.get_safe("fPIC", True)
        self._autotools_env = self._autotools.vars
        self._autotools_env["SHARED"] = \
            "yes" if self.options.shared else "no"
        self._autotools_env["PTHREADS"] = \
            "yes" if self.options.psx_syscals else "no"
        self._autotools_env["DESTDIR"] = self.package_folder
        self._autotools_env["prefix"] = "/"
        self._autotools_env["lib"] = "lib"

        if tools.build.cross_building(self, self.settings) and not tools.get_env("BUILD_CC"):
            native_cc = tools.which("cc")
            self.output.info("Using native compiler '{}'".format(native_cc))
            self._autotools_env["BUILD_CC"] = native_cc

        return self._autotools, self._autotools_env

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()

        with tools.files.chdir(self, os.path.join(self._source_subfolder, self.name)):
            env_build, env_build_vars = self._configure_autotools()
            env_build.make(vars=env_build_vars)

    def package(self):
        self.copy("License", dst="licenses", src=self._source_subfolder)

        with tools.files.chdir(self, os.path.join(self._source_subfolder, self.name)):
            env_build, env_build_vars = self._configure_autotools()

            env_build.make(target="install-common-cap", vars=env_build_vars)
            install_cap = ("install-shared-cap" if self.options.shared
                           else "install-static-cap")
            env_build.make(target=install_cap, vars=env_build_vars)

            if self.options.psx_syscals:
                env_build.make(target="install-common-psx",
                               vars=env_build_vars)
                install_psx = ("install-shared-psx" if self.options.shared
                               else "install-static-psx")
                env_build.make(target=install_psx, vars=env_build_vars)

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["cap"].names["pkg_config"] = "libcap"
        self.cpp_info.components["cap"].libs = ["cap"]
        if self.options.psx_syscals:
            self.cpp_info.components["psx"].names["pkg_config"] = "libpsx"
            self.cpp_info.components["psx"].libs = ["psx"]
            self.cpp_info.components["psx"].system_libs = ["pthread"]
            self.cpp_info.components["psx"].exelinkflags = [
                "-Wl,-wrap,pthread_create"]
