from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file, rename, rm, rmdir
from conan.tools.microsoft import MSBuild, MSBuildDeps, MSBuildToolchain, is_msvc, check_min_vs, unix_path, vs_layout
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import glob
import os
import shutil

required_conan_version = ">=1.55.0"


class LibdbConan(ConanFile):
    name = "libdb"
    description = "Berkeley DB is a family of embedded key-value database libraries providing scalable high-performance data management services to applications"
    topics = ("gdbm", "dbm", "hash", "database")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.oracle.com/database/berkeley-db"
    license = ("BSD-3-Clause")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tcl": [True, False],
        "with_cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tcl": False,
        "with_cxx": False,
    }


    @property
    def _mingw_build(self):
        return self.settings.compiler == "gcc" and self.settings.os == "Windows"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.options.rm_safe("with_cxx")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("with_cxx", False):
            self.settings.compiler.rm_safe("libcxx")
            self.settings.compiler.rm_safe("cppstd")

    def requirements(self):
        if self.options.with_tcl:
            self.requires("tcl/8.6.10")

    def validate(self):
        if is_msvc(self) and check_min_vs(self, "191", raise_invalid=False):
            # FIXME: it used to work with previous versions of Visual Studio 2019 in CI of CCI.
            raise ConanInvalidConfiguration(f"{self.ref} Visual Studio 2019 is currently not supported. Contributions are welcomed!")
            
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration(f"{self.ref} Macos Apple Sillicon is currently not supported. Contributions are welcomed!")

        if self.options.get_safe("with_cxx"):
            if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration(f"{self.ref} does not support clang<6 with_cxx=True")
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "10":
                raise ConanInvalidConfiguration(f"{self.ref} does not support apple-clang<10 with_cxx=True")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        else:
            self.tool_requires("gnu-config/cci.20201022")

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

        if not is_msvc(self):
            for subdir in [
                "dist",
                os.path.join("lang", "sql", "jdbc"),
                os.path.join("lang", "sql", "odbc"),
                os.path.join("lang", "sql", "sqlite"),
            ]:
                shutil.copy(self.dependencies.build["gnu-config"].conf_info.get("user.gnu-config:config_sub"),
                            os.path.join(self.source_folder, subdir, "config.sub"))
                shutil.copy(self.dependencies.build["gnu-config"].conf_info.get("user.gnu-config:config_guess"),
                            os.path.join(self.source_folder, subdir, "config.guess"))

        for file in glob.glob(os.path.join(self.source_folder, "build_windows", "VS10", "*.vcxproj")):
            replace_in_file(self, file,
                                  "<PropertyGroup Label=\"Globals\">",
                                  "<PropertyGroup Label=\"Globals\"><WindowsTargetPlatformVersion>10.0.17763.0</WindowsTargetPlatformVersion>")

        dist_configure = os.path.join(self.source_folder, "dist", "configure")
        replace_in_file(self, dist_configure, "../$sqlite_dir", "$sqlite_dir")
        replace_in_file(self, dist_configure,
                              "\n    --disable-option-checking)",
                              "\n    --datarootdir=*)"
                              "\n      ;;"
                              "\n    --disable-option-checking)")

    # def _build_msvc(self):
    #     projects = ["db", "db_sql", "db_stl"]
    #     if self.options.with_tcl:
    #         projects.append("db_tcl")
    #     msbuild = MSBuild(self)
    #     upgraded = False
    #     for project in projects:
    #         msbuild.build(os.path.join(self.source_folder, "build_windows", "VS10", "{}.vcxproj".format(project)),
    #                       build_type=self._msvc_build_type, platforms=self._msvc_platforms,
    #                       upgrade_project=not upgraded)
    #         upgraded = True

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()

            deps = MSBuildDeps(self)

            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug")
            tc.configure_args.append("--enable-mingw" if self._mingw_build else "--disable-mingw")
            tc.configure_args.append("--enable-compat185")
            tc.configure_args.append("--enable-sql")
            if self.options.with_cxx:
                tc.configure_args.extend(["--enable-cxx", "--enable-stl"])
            else:
                tc.configure_args.extend(["--disable-cxx", "--disable-stl"])

            if self.options.shared:
                tc.configure_args.extend(["--enable-shared", "--disable-static"])
            else:
                tc.configure_args.extend(["--disable-shared", "--enable-static"])

            if self.options.with_tcl:
                tc.configure_args.append(f"--with-tcl={os.path.join(self.dependencies['tcl'].package_folder, 'lib')}")
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()


    @property
    def _msvc_build_type(self):
        return ("" if self.options.shared else "Static ") + ("Debug" if self.settings.build_type == "Debug" else "Release")

    _msvc_platforms = {
        "x86": "win32",
        "x86_64": "x64",
    }

    @property
    def _msvc_arch(self):
        return self._msvc_platforms[str(self.settings.arch)]

    # def _build_msvc(self):
    #     projects = ["db", "db_sql", "db_stl"]
    #     if self.options.with_tcl:
    #         projects.append("db_tcl")
    #     msbuild = MSBuild(self)
    #     upgraded = False
    #     for project in projects:
    #         msbuild.build(os.path.join(self.source_folder, "build_windows", "VS10", "{}.vcxproj".format(project)),
    #                       build_type=self._msvc_build_type, platforms=self._msvc_platforms,
    #                       upgrade_project=not upgraded)
    #         upgraded = True

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            #self._build_msvc()
            projects = ["db", "db_sql", "db_stl"]
            if self.options.with_tcl:
                projects.append("db_tcl")
            msbuild = MSBuild(self)
            for project in projects:
                msbuild.build(sln=os.path.join(self.source_folder, "build_windows", "VS10", f"{project}.vcxproj"))
        else:
            autotools = Autotools(self)
            autotools.configure(build_script_folder=os.path.join(self.source_folder, "dist"))
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        bindir = os.path.join(self.package_folder, "bin")
        libdir = os.path.join(self.package_folder, "lib")
        if is_msvc(self):
            build_windows = os.path.join(self.source_folder, "build_windows")
            build_dir = os.path.join(self.source_folder, "build_windows", self._msvc_arch, self._msvc_build_type)
            copy(self, "*.lib", src=build_dir, dst=libdir)
            copy(self, "*.dll", src=build_dir, dst=bindir)
            for fn in ("db.h", "db.cxx", "db_int.h", "dbstl_common.h"):
                copy(self, fn, src=build_windows, dst=os.path.join(self.package_folder, "include"))

            def _lib_to_msvc_lib(lib):
                shared_suffix = "" if self.options.shared else "s"
                debug_suffix = "d" if self.settings.build_type == "Debug" else ""
                version_suffix = "".join(self._major_minor_version)
                return "{}{}{}{}".format(lib, version_suffix, shared_suffix, debug_suffix)

            msvc_libs = [_lib_to_msvc_lib(lib) for lib in self._libs]
            for lib, msvc_lib in zip(self._libs, msvc_libs):
                rename(self, os.path.join(libdir, "{}.lib".format(msvc_lib)),
                             os.path.join(libdir, "{}.lib".format(lib)))
        else:
            autotools = Autotools(self)
            autotools.install()

            if self.settings.os == "Windows":
                for fn in os.listdir(libdir):
                    if fn.endswith(".dll"):
                        rename(self, os.path.join(libdir, fn), os.path.join(bindir, fn))
                for fn in os.listdir(bindir):
                    if not fn.endswith(".dll"):
                        binpath = os.path.join(bindir, fn)
                        os.chmod(binpath, 0o755)  # Fixes PermissionError(errno.EACCES) on mingw
                        os.remove(binpath)
                if self.options.shared:
                    dlls = ["lib{}-{}.dll".format(lib, ".".join(self._major_minor_version)) for lib in self._libs]
                    for fn in os.listdir(bindir):
                        if fn not in dlls:
                            print("removing", fn, "in bin")
                            os.remove(os.path.join(bindir, fn))

                if not os.listdir(bindir):
                    rmdir(self, bindir)

            rmdir(self, os.path.join(self.package_folder, "docs"))
            rm(self, "*.la", libdir)
            if not self.options.shared:
                # autotools installs the static libraries twice as libXXX.a and libXXX-5.3.a ==> remove libXXX-5.3.a
                rm(self, "*-{}.a".format(".".join(self._major_minor_version)), libdir)

    @property
    def _major_minor_version(self):
        [major, minor, _] = self.version.split(".", 2)
        return major, minor

    @property
    def _libs(self):
        libs = []
        if self.options.with_tcl:
            libs.append("db_tcl")
        if self.options.get_safe("with_cxx"):
            libs.extend(["db_cxx", "db_stl"])
        libs.extend(["db_sql", "db"])
        if is_msvc(self):
            libs = [f"lib{libname}" for libname in libs]
        return libs

    def package_info(self):
        self.cpp_info.libs = self._libs
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines = ["DB_USE_DLL"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
