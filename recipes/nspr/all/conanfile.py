import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rmdir, mkdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag, unix_path_package_info_legacy
from conan.tools.scm import Version

required_conan_version = ">=1.57.0"


class NsprConan(ConanFile):
    name = "nspr"
    description = ("Netscape Portable Runtime (NSPR) provides a platform-neutral API"
                   " for system level and libc-like functions.")
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR"
    topics = ("libc",)

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mozilla": [True, False],
        "win32_target": ["winnt", "win95"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mozilla": True,
        "win32_target": "winnt",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            self.options.rm_safe("win32_target")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1658671
        if Version(self.version) < "4.29":
            if is_apple_os(self) and self.settings.arch == "armv8":
                raise ConanInvalidConfiguration("NSPR does not support mac M1 before 4.29")
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross-building is not supported")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("mozilla-build/3.3")
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        with chdir(self, self.export_sources_folder):
            get(self, **self.conan_data["sources"][self.version], strip_root=True)
            rmdir(self, self.source_folder)
            rename(self, "nspr", self.source_folder)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--with-mozilla={}".format(yes_no(self.options.with_mozilla)),
            "--enable-64bit={}".format(yes_no(self.settings.arch in ("armv8", "x86_64", "mips64", "ppc64", "ppc64le"))),
            "--enable-strip={}".format(yes_no(self.settings.build_type not in ("Debug", "RelWithDebInfo"))),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--datarootdir=${prefix}/res",
            "--disable-cplus",
        ]
        if is_msvc(self):
            tc.configure_args += [
                "{}-pc-mingw32".format("x86_64" if self.settings.arch == "x86_64" else "x86"),
                "--enable-static-rtl={}".format(yes_no(is_msvc_static_runtime(self))),
                "--enable-debug-rtl={}".format(yes_no("d" in msvc_runtime_flag(self))),
            ]
        elif self.settings.os == "Android":
            tc.configure_args += [
                "--with-android-ndk={}".format(os.environ.get("NDK_ROOT", "")),
                "--with-android-version={}".format(self.settings.os.api_level),
                "--with-android-platform={}".format(os.environ.get("ANDROID_PLATFORM")),
                "--with-android-toolchain={}".format(os.environ.get("ANDROID_TOOLCHAIN")),
            ]
        elif self.settings.os == "Windows":
            tc.configure_args.append("--enable-win32-target={}".format(self.options.win32_target))
        if is_apple_os(self) and self.settings.arch == "armv8":
            # conan adds `-arch`, which conflicts with nspr's apple silicon support
            tc.cflags.remove("-arch arm64")
            tc.cxxflags.remove("-arch arm64")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl")
            env.define("CXX", "cl")
            env.define("LD", "link")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        with chdir(self, self.source_folder):
            # relocatable shared libs on macOS
            replace_in_file(self, "configure", "-install_name @executable_path/", "-install_name @rpath/")
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if os.path.exists(os.path.join(self.package_folder, "include", "nspr.h")):
            with chdir(self, self.package_folder):
                rename(self, "include", "nspr")
                mkdir(self, "include")
                shutil.move("nspr", "include")
        if self.settings.os == "Windows":
            if self.options.shared:
                os.mkdir(os.path.join(self.package_folder, "bin"))
            for lib in self._library_names:
                libsuffix = "lib" if is_msvc(self) else "a"
                libprefix = "" if is_msvc(self) else "lib"
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", f"{libprefix}{lib}_s.{libsuffix}"))
                    rename(self,
                           os.path.join(self.package_folder, "lib", f"{lib}.dll"),
                           os.path.join(self.package_folder, "bin", f"{lib}.dll"))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", f"{libprefix}{lib}.{libsuffix}"))
                    os.unlink(os.path.join(self.package_folder, "lib", f"{lib}.dll"))
            if not self.options.shared:
                replace_in_file(self, os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                "#define NSPR_API(__type) PR_IMPORT(__type)",
                                "#define NSPR_API(__type) extern __type")
                replace_in_file(self, os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                "#define NSPR_DATA_API(__type) PR_IMPORT_DATA(__type)",
                                "#define NSPR_DATA_API(__type) extern __type")
        else:
            shared_ext = "dylib" if is_apple_os(self) else "so"
            for lib in self._library_names:
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", f"lib{lib}.a"))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", f"lib{lib}.{shared_ext}"))

        if is_msvc(self):
            if self.settings.build_type == "Debug":
                for lib in self._library_names:
                    os.unlink(os.path.join(self.package_folder, "lib", f"{lib}.pdb"))

        if not self.options.shared or self.settings.os == "Windows":
            for f in os.listdir(os.path.join(self.package_folder, "lib")):
                os.chmod(os.path.join(self.package_folder, "lib", f), 0o644)

    @property
    def _library_names(self):
        return ["plds4", "plc4", "nspr4"]

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "nspr")
        libs = self._library_names
        if self.settings.os == "Windows" and not self.options.shared:
            libs = list(f"{l}_s" for l in libs)
        self.cpp_info.libs = libs
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            if self.settings.arch == "x86":
                self.cpp_info.defines.append("_M_IX86")
            elif self.settings.arch == "x86_64":
                self.cpp_info.defines.append("_M_X64")
        self.cpp_info.includedirs.append(os.path.join("include", "nspr"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ws2_32"])

        self.cpp_info.resdirs = ["res"]

        # TODO: the following can be removed when the recipe supports Conan >= 2.0 only
        aclocal = unix_path_package_info_legacy(self, os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info(f"Appending AUTOMAKE_CONAN_INCLUDES environment variable: {aclocal}")
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)
