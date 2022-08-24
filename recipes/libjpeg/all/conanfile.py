from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import re
import shutil

required_conan_version = ">=1.43.0"


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("image", "format", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = "IJG"
    homepage = "http://ijg.org"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang_cl(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    def export_sources(self):
        self.copy("Win32.Mak")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not (self._is_msvc or self. _is_clang_cl) and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_nmake(self):
        shutil.copy("Win32.Mak", os.path.join(self._source_subfolder, "Win32.Mak"))
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Win32.Mak"),
                              "\nccommon = -c ",
                              "\nccommon = -c -DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC "))
        # clean environment variables that might affect on the build (e.g. if set by Jenkins)
        with tools.files.chdir(self, self._source_subfolder), tools.environment_append({"PROFILE": None, "TUNE": None, "NODEBUG": None}):
            shutil.copy("jconfig.vc", "jconfig.h")
            make_args = [
                "nodebug=1" if self.settings.build_type != 'Debug' else "",
            ]
            if self._is_clang_cl:
                cl = os.environ.get('CC', 'clang-cl')
                link = os.environ.get('LD', 'lld-link')
                lib = os.environ.get('AR', 'llvm-lib')
                rc = os.environ.get('RC', 'llvm-rc')
                tools.files.replace_in_file(self, 'Win32.Mak', 'cc     = cl', 'cc     = %s' % cl)
                tools.files.replace_in_file(self, 'Win32.Mak', 'link   = link', 'link   = %s' % link)
                tools.files.replace_in_file(self, 'Win32.Mak', 'implib = lib', 'implib = %s' % lib)
                tools.files.replace_in_file(self, 'Win32.Mak', 'rc     = Rc', 'rc     = %s' % rc)
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if self.settings.compiler.runtime in ["MD", "MDd"]:
                tools.files.replace_in_file(self, "makefile.vc", "(cvars)", "(cvarsdll)")
                tools.files.replace_in_file(self, "makefile.vc", "(conlibs)", "(conlibsdll)")
            else:
                tools.files.replace_in_file(self, "makefile.vc", "(cvars)", "(cvarsmt)")
                tools.files.replace_in_file(self, "makefile.vc", "(conlibs)", "(conlibsmt)")
            target = "{}/libjpeg.lib".format( "shared" if self.options.shared else "static" )
            with tools.vcvars(self.settings):
                self.run("nmake -f makefile.vc {} {}".format(" ".join(make_args), target))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.defines.append("LIBJPEG_BUILDING")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Fix rpath in LC_ID_DYLIB of installed shared libs on macOS
        if tools.apple.is_apple_os(self, self.settings.os):
            tools.files.replace_in_file(self, 
                os.path.join(self._source_subfolder, "configure"),
                "-install_name \\$rpath/",
                "-install_name @rpath/",
            )

    def build(self):
        self._patch_sources()
        if self._is_msvc or self._is_clang_cl:
            self._build_nmake()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("README", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if (self._is_msvc or self._is_clang_cl):
            for filename in ["jpeglib.h", "jerror.h", "jconfig.h", "jmorecfg.h"]:
                self.copy(pattern=filename, dst="include", src=self._source_subfolder, keep_path=False)

            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            if self.settings.os == "Windows" and self.options.shared:
                tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*[!.dll]")
            else:
                tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        for fn in ("jpegint.h", "transupp.h",):
            self.copy(fn, src=self._source_subfolder, dst="include")

        for fn in ("jinclude.h", "transupp.c",):
            self.copy(fn, src=self._source_subfolder, dst="res")

        # Remove export decorations of transupp symbols
        for relpath in os.path.join("include", "transupp.h"), os.path.join("res", "transupp.c"):
            path = os.path.join(self.package_folder, relpath)
            tools.files.save(self, path, re.subn(r"(?:EXTERN|GLOBAL)\(([^)]+)\)", r"\1", tools.files.load(self, path))[0])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "JPEG")
        self.cpp_info.set_property("cmake_target_name", "JPEG::JPEG")
        self.cpp_info.set_property("pkg_config_name", "libjpeg")

        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "JPEG"

        if (self._is_msvc or self._is_clang_cl):
            self.cpp_info.libs = ["libjpeg"]
        else:
            self.cpp_info.libs = ["jpeg"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")
