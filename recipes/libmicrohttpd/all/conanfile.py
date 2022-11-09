from conan import ConanFile, Version
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, vs_layout
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class LibmicrohttpdConan(ConanFile):
    name = "libmicrohttpd"
    description = "A small C library that is supposed to make it easy to run an HTTP server"
    homepage = "https://www.gnu.org/software/libmicrohttpd/"
    topics = ("httpd", "server", "service")
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os != "Linux":
            try:
                del self.options.fPIC
            except Exception:
                pass
            del self.options.epoll
        if is_msvc(self):
            del self.options.with_https
            del self.options.with_error_messages
            del self.options.with_postprocessor
            del self.options.with_digest_authentification
            del self.options.with_zlib

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
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msvc_configuration
            tc.generate()
        else:
            yes_no = lambda v: "yes" if v else "no"
            pkg = PkgConfigDeps(self)
            pkg.generate()
            autotools = AutotoolsToolchain(self)
            autotools.configure_args.extend([
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
            if self.settings.os == "Windows":
                if self.options.with_zlib:
                    # This fixes libtool refusing to build a shared library when it sees `-lz`
                    libdir = self.deps_cpp_info["zlib"].lib_paths[0]
                    autotools.extra_ldflags.extend([os.path.join(libdir, lib).replace("\\", "/") for lib in os.listdir(libdir)])
            autotools.generate()

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
    def _msvc_platform(self):
        return {
            "x86": "Win32",
            "x86_64": "x64",
        }[str(self.settings.arch)]

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build_type = self._msvc_configuration
            msbuild.platform = self._msvc_platform
            msbuild.build(sln=os.path.join(self._msvc_sln_folder, "libmicrohttpd.sln"), targets=["libmicrohttpd"])
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", os.path.join(self.source_folder), os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            # 32-bit (x86) libraries are stored in the root
            output_dir = os.path.join(self.build_folder, self._msvc_sln_folder, "Output")
            if self.settings.arch in ("x86_64", ):
                # 64-bit (x64) libraries are stored in a subfolder
                output_dir = os.path.join(output_dir, self._msvc_platform)
            copy(self, "*.lib", output_dir, os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", output_dir, os.path.join(self.package_folder, "bin"))
            copy(self, "*.h", output_dir, os.path.join(self.package_folder, "include"))
        else:
            autotools = Autotools(self)
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
