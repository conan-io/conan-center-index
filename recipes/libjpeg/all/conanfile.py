from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import re
import shutil

required_conan_version = ">=1.33.0"


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "image", "format", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = "http://ijg.org/files/README"
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

    exports_sources = ["Win32.Mak", "patches/**"]
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_nmake(self):
        shutil.copy("Win32.Mak", os.path.join(self._source_subfolder, "Win32.Mak"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "Win32.Mak"),
                              "\nccommon = -c ",
                              "\nccommon = -c -DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC "))
        with tools.chdir(self._source_subfolder):
            shutil.copy("jconfig.vc", "jconfig.h")
            make_args = [
                "nodebug=1" if self.settings.build_type != 'Debug' else "",
            ]
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if self.settings.compiler.runtime in ["MD", "MDd"]:
                tools.replace_in_file("makefile.vc", "(cvars)", "(cvarsdll)")
                tools.replace_in_file("makefile.vc", "(conlibs)", "(conlibsdll)")
            else:
                tools.replace_in_file("makefile.vc", "(cvars)", "(cvarsmt)")
                tools.replace_in_file("makefile.vc", "(conlibs)", "(conlibsmt)")
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
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_nmake()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("README", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        if self.settings.compiler == "Visual Studio":
            for filename in ["jpeglib.h", "jerror.h", "jconfig.h", "jmorecfg.h"]:
                self.copy(pattern=filename, dst="include", src=self._source_subfolder, keep_path=False)

            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            if self.settings.os == "Windows" and self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*[!.dll]")
            else:
                tools.rmdir(os.path.join(self.package_folder, "bin"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

        for fn in ("jpegint.h", "transupp.h",):
            self.copy(fn, src=self._source_subfolder, dst="include")

        for fn in ("jinclude.h", "transupp.c",):
            self.copy(fn, src=self._source_subfolder, dst="res")

        # Remove export decorations of transupp symbols
        for relpath in os.path.join("include", "transupp.h"), os.path.join("res", "transupp.c"):
            path = os.path.join(self.package_folder, relpath)
            tools.save(path, re.subn(r"(?:EXTERN|GLOBAL)\(([^)]+)\)", r"\1", tools.load(path))[0])

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "JPEG"
        self.cpp_info.names["pkg_config"] = "libjpeg"
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["libjpeg"]
        else:
            self.cpp_info.libs = ["jpeg"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")
