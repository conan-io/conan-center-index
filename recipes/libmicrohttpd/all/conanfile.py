from conan import ConanFile, Version
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, vs_layout
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment
import functools
import os

required_conan_version = ">=1.52.0"


class LibmicrohttpdConan(ConanFile):
    name = "libmicrohttpd"
    description = "A small C library that is supposed to make it easy to run an HTTP server"
    homepage = "https://www.gnu.org/software/libmicrohttpd/"
    topics = ("libmicrohttpd", "httpd", "server", "service")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_https": [True, False],
        "with_error_messages": [True, False],
        "with_postprocessor": [True, False],
        "with_digest_authentification": [True, False],
        "epoll": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_https": False,  # FIXME: should be True, but gnutls is not yet available in cci
        "with_error_messages": True,
        "with_postprocessor": True,
        "with_digest_authentification": True,
        "epoll": True,
        "with_zlib": True,
    }
    generators = "pkg_config"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.fPIC
            del self.options.epoll
        if is_msvc(self):
            del self.options.with_https
            del self.options.with_error_messages
            del self.options.with_postprocessor
            del self.options.with_digest_authentification
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def validate(self):
        if is_msvc(self):
            if self.info.settings.arch not in ("x86", "x86_64"):
                raise ConanInvalidConfiguration("Unsupported architecture (only x86 and x86_64 are supported)")
            if self.info.settings.build_type not in ("Release", "Debug"):
                raise ConanInvalidConfiguration("Unsupported build type (only Release and Debug are supported)")

    def requirements(self):
        if self.options.get_safe("with_zlib", False):
            self.requires("zlib/1.2.13")
        if self.options.get_safe("with_https", False):
            raise ConanInvalidConfiguration("gnutls is not (yet) available in cci")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self) and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
            self.build_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        if is_msvc(self):
            vs_layout(self)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msvc_configuration
            tc.generate()

    @property
    def _msvc_configuration(self):
        return f"{self.settings.build_type}-{'dll' if self.options.shared else 'static'}"

    @property
    def _msvc_sln_folder(self):
        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version) >= 16:
                subdir = "VS-Any-Version"
            else:
                subdir = "VS2017"
        else:
            subdir = "VS-Any-Version"
        return os.path.join("w32", subdir)

    @property
    def _msvc_arch(self):
        return {
            "x86": "Win32",
            "x86_64": "x64",
        }[str(self.settings.arch)]

    def _patch_sources(self):
        apply_conandata_patches(self)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        yes_no = lambda v: "yes" if v else "no"
        autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        autotools.libs = []
        if self.settings.os == "Windows":
            if self.options.with_zlib:
                libdir = self.deps_cpp_info["zlib"].lib_paths[0]
                autotools.link_flags.extend([os.path.join(libdir, lib).replace("\\", "/") for lib in os.listdir(libdir)])
        autotools.configure(self.source_folder,[
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            f"--enable-https={yes_no(self.options.with_https)}",
            f"--enable-messages={yes_no(self.options.with_error_messages)}",
            f"--enable-postprocessor={yes_no(self.options.with_postprocessor)}",
            f"--enable-dauth={yes_no(self.options.with_digest_authentification)}",
            f"--enable-epoll={yes_no(self.options.get_safe('epoll'))}",
            "--disable-doc",
            "--disable-examples",
            "--disable-curl",
        ])
        return autotools

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build_type = self._msvc_configuration
            msbuild.build(sln=os.path.join(self._msvc_sln_folder, "libmicrohttpd.sln"), targets=["libmicrohttpd"])
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        copy(self, "COPYING", os.path.join(self.build_folder), os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "*.lib", os.path.join(self.build_folder, self._msvc_sln_folder, "Output", self._msvc_arch), os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", os.path.join(self.build_folder, self._msvc_sln_folder, "Output", self._msvc_arch), os.path.join(self.package_folder, "bin"))
            copy(self, "*.h", os.path.join(self.build_folder, self._msvc_sln_folder, "Output", self._msvc_arch), os.path.join(self.package_folder, "include"))
        else:
            autotools = self._configure_autotools()
            autotools.install()

            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmicrohttps")
        libname = "microhttpd"
        if is_msvc(self):
            libname = "libmicrohttpd"
            if self.options.shared:
                libname += "-dll"
            if self.settings.build_type == "Debug":
                libname += "_d"
        self.cpp_info.libs = [libname]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("MHD_W32DLL")
            self.cpp_info.system_libs = ["ws2_32"]
