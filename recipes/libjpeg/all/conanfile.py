import os
import re
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "image", "format", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = "http://ijg.org/files/README"
    homepage = "http://ijg.org"
    exports_sources = ["Win32.Mak", "patches/**"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("jpeg-" + self.version, self._source_subfolder)

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
        """For unix and mingw environments"""
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.defines.append("LIBJPEG_BUILDING")
        config_args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])

        if self.settings.os == "Windows":
            mingw_arch = {
                "x86_64": "x86_64",
                "x86": "i686",
            }
            build_triplet = host_triplet = "{}-w64-mingw32".format(mingw_arch[str(self.settings.arch)])
            config_args.extend([
                "--build={}".format(build_triplet),
                "--host={}".format(host_triplet),
            ])

        self._autotools.configure(configure_dir=self._source_subfolder, args=config_args)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
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
            os.unlink(os.path.join(self.package_folder, "lib", "libjpeg.la"))

            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

            bindir = os.path.join(self.package_folder, "bin")
            for file in os.listdir(bindir):
                if file.endswith(".exe"):
                    os.unlink(os.path.join(bindir, file))

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
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["libjpeg"]
        else:
            self.cpp_info.libs = ["jpeg"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")
