from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.43.0"


class GiflibConan(ConanFile):
    name = "giflib"
    description = "A library and utilities for reading and writing GIF images."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://giflib.sourceforge.net"
    topics = ("giflib", "image", "multimedia", "format", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # The exported files I took them from https://github.com/bjornblissing/osg-3rdparty-cmake/tree/master/giflib
    # refactored a little
    exports_sources = ["unistd.h", "gif_lib.h"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        # disable util build - tools and internal libs
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                              "SUBDIRS = lib util pic $(am__append_1)",
                              "SUBDIRS = lib pic $(am__append_1)")

        if self._is_msvc:
            self.build_visual()
        else:
            self.build_configure()

    def build_visual(self):
        # fully replace gif_lib.h for VS, with patched version
        ver_components = self.version.split(".")
        tools.files.replace_in_file(self, "gif_lib.h", "@GIFLIB_MAJOR@", ver_components[0])
        tools.files.replace_in_file(self, "gif_lib.h", "@GIFLIB_MINOR@", ver_components[1])
        tools.files.replace_in_file(self, "gif_lib.h", "@GIFLIB_RELEASE@", ver_components[2])
        shutil.copy("gif_lib.h", os.path.join(self._source_subfolder, "lib"))
        # add unistd.h for VS
        shutil.copy("unistd.h", os.path.join(self._source_subfolder, "lib"))

        with tools.chdir(self._source_subfolder):
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
            else:
                raise ConanInvalidConfiguration("unsupported architecture %s" % self.settings.arch)
            if self.options.shared:
                options = "--disable-static --enable-shared"
            else:
                options = "--enable-static --disable-shared"

            cflags = ""
            if not self.options.shared:
                cflags = "-DUSE_GIF_LIB"

            prefix = tools.unix_path(os.path.abspath(self.package_folder))
            with tools.vcvars(self.settings):
                command = "./configure " \
                          "{options} " \
                          "--host={host} " \
                          "--prefix={prefix} " \
                          'CC="$PWD/compile cl -nologo" ' \
                          'CFLAGS="-{runtime} {cflags}" ' \
                          'CXX="$PWD/compile cl -nologo" ' \
                          'CXXFLAGS="-{runtime} {cflags}" ' \
                          'CPPFLAGS="-I{prefix}/include" ' \
                          'LDFLAGS="-L{prefix}/lib" ' \
                          'LD="link" ' \
                          'NM="dumpbin -symbols" ' \
                          'STRIP=":" ' \
                          'AR="$PWD/ar-lib lib" ' \
                          'RANLIB=":" '.format(host=host, prefix=prefix, options=options,
                                               runtime=self.settings.compiler.runtime, cflags=cflags)
                self.run(command, win_bash=True)
                self.run("make", win_bash=True)
                self.run("make install", win_bash=True)

    def build_configure(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        with tools.chdir(self._source_subfolder):
            if tools.is_apple_os(self.settings.os):
                # relocatable shared lib on macOS
                tools.files.replace_in_file(self, 
                    "configure",
                    "-install_name \\$rpath/\\$soname",
                    "-install_name \\@rpath/\\$soname"
                )

            self.run("chmod +x configure")
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=["install"])

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=False)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self._is_msvc and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "gif.dll.lib"),
                         os.path.join(self.package_folder, "lib", "gif.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GIF")
        self.cpp_info.set_property("cmake_target_name", "GIF::GIF")

        self.cpp_info.names["cmake_find_package"] = "GIF"
        self.cpp_info.names["cmake_find_package_multi"] = "GIF"

        self.cpp_info.libs = ["gif"]
        if self._is_msvc:
            self.cpp_info.defines.append("USE_GIF_DLL" if self.options.shared else "USE_GIF_LIB")
