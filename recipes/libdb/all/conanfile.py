from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class LibdbConan(ConanFile):
    name = "libdb"
    description = "Berkeley DB is a family of embedded key-value database libraries providing scalable high-performance data management services to applications"
    topics = ("conan", "gdbm", "dbm", "hash", "database")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.oracle.com/database/berkeley-db"
    license = ("BSD-3-Clause")
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
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

    generators = "visual_studio"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _mingw_build(self):
        return self.settings.compiler == "gcc" and self.settings.os == "Windows"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            del self.options.with_cxx

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.get_safe("with_cxx"):
            if self.settings.compiler == "clang":
                if self.settings.compiler.version <= tools.Version("5"):
                    raise ConanInvalidConfiguration("This compiler version is unsupported")
            if self.settings.compiler == "apple-clang":
                if self.settings.compiler.version < tools.Version("10"):
                    raise ConanInvalidConfiguration("This compiler version is unsupported")

    def requirements(self):
        if self.options.with_tcl:
            self.requires("tcl/8.6.10")

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ and \
                    tools.os_info.detect_windows_subsystem() != "msys2":
                self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("db-{}".format(self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch_data in self.conan_data["patches"][self.version]:
            tools.patch(**patch_data)

        import glob
        for file in glob.glob(os.path.join(self._source_subfolder, "build_windows", "VS10", "*.vcxproj")):
            tools.replace_in_file(file,
                                  "<PropertyGroup Label=\"Globals\">",
                                  "<PropertyGroup Label=\"Globals\"><WindowsTargetPlatformVersion>10.0.17763.0</WindowsTargetPlatformVersion>")

        dist_configure = os.path.join(self._source_subfolder, "dist", "configure")
        tools.replace_in_file(dist_configure, "../$sqlite_dir", "$sqlite_dir")
        tools.replace_in_file(dist_configure,
                              "\n    --disable-option-checking)",
                              "\n    --datarootdir=*)"
                              "\n      ;;"
                              "\n    --disable-option-checking)")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-mingw" if self._mingw_build else "--disable-mingw",
            "--enable-compat185",
            "--enable-sql",
        ]
        if self.options.with_cxx:
            conf_args.extend(["--enable-cxx", "--enable-stl"])
        else:
            conf_args.extend(["--disable-cxx", "--disable-stl"])

        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        if self.options.with_tcl:
            conf_args.append("--with-tcl={}".format(tools.unix_path(os.path.join(self.deps_cpp_info["tcl"].rootpath, "lib"))))
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder, "dist"), args=conf_args)
        if self.settings.os == "Windows" and self.options.shared:
            tools.replace_in_file(os.path.join(self.build_folder, "libtool"),
                                  "\ndeplibs_check_method=",
                                  "\ndeplibs_check_method=pass_all\n#deplibs_check_method=")
            tools.replace_in_file(os.path.join(self.build_folder, "Makefile"),
                                  ".a",
                                  ".dll.a")
        return self._autotools

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

    def _build_msvc(self):
        projects = ["db", "db_sql", "db_stl"]
        if self.options.with_tcl:
            projects.append("db_tcl")
        msbuild = MSBuild(self)
        upgraded = False
        for project in projects:
            msbuild.build(os.path.join(self._source_subfolder, "build_windows", "VS10", "{}.vcxproj".format(project)),
                          build_type=self._msvc_build_type, platforms=self._msvc_platforms,
                          upgrade_project=not upgraded)
            upgraded = True

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        bindir = os.path.join(self.package_folder, "bin")
        libdir = os.path.join(self.package_folder, "lib")
        if self.settings.compiler == "Visual Studio":
            build_windows = os.path.join(self._source_subfolder, "build_windows")
            build_dir = os.path.join(self._source_subfolder, "build_windows", self._msvc_arch, self._msvc_build_type)
            self.copy("*.lib", src=build_dir, dst="lib")
            self.copy("*.dll", src=build_dir, dst="bin")
            for fn in ("db.h", "db.cxx", "db_int.h", "dbstl_common.h"):
                self.copy(fn, src=build_windows, dst="include")

            def _lib_to_msvc_lib(lib):
                shared_suffix = "" if self.options.shared else "s"
                debug_suffix = "d" if self.settings.build_type == "Debug" else ""
                version_suffix = "".join(self._major_minor_version)
                return "{}{}{}{}".format(lib, version_suffix, shared_suffix, debug_suffix)

            msvc_libs = [_lib_to_msvc_lib(lib) for lib in self._libs]
            for lib, msvc_lib in zip(self._libs, msvc_libs):
                os.rename(os.path.join(libdir, "{}.lib".format(msvc_lib)),
                          os.path.join(libdir, "{}.lib".format(lib)))
        else:
            autotools = self._configure_autotools()
            autotools.install()

            if self.settings.os == "Windows":
                for fn in os.listdir(libdir):
                    if fn.endswith(".dll"):
                        os.rename(os.path.join(libdir, fn), os.path.join(bindir, fn))
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
                    tools.rmdir(bindir)

            for lib in self._libs:
                la_file = os.path.join(libdir, "lib{}-{}.la".format(lib, ".".join(self._major_minor_version)))
                if os.path.exists(la_file):
                    os.remove(la_file)
                if not self.options.shared:
                    # autotools installs the static libraries twice as libXXX.a and libXXX-5.3.a ==> remove libXXX-5.3.a
                    libfn = os.path.join(libdir, "lib{}.a".format(lib))
                    lib_version_fn = os.path.join(libdir, "lib{}-{}.a".format(lib, ".".join(self._major_minor_version)))
                    assert os.path.isfile(libfn)
                    os.remove(lib_version_fn)

            tools.rmdir(os.path.join(self.package_folder, "docs"))

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
        if self.settings.compiler == "Visual Studio":
            libs = ["lib{}".format(lib) for lib in libs]
        return libs

    def package_info(self):
        self.cpp_info.libs = self._libs
        if self.settings.compiler == "Visual Studio"and self.options.shared:
            self.cpp_info.defines = ["DB_USE_DLL"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows" :
            self.cpp_info.system_libs.append("ws2_32")

