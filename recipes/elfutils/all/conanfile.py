from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class ElfutilsConan(ConanFile):
    name = "elfutils"
    description = "A dwarf, dwfl and dwelf functions to read DWARF, find separate debuginfo, symbols and inspect process state."
    homepage = "https://sourceware.org/elfutils"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "elfutils", "libelf", "libdw", "libasm")
    exports = "patches/**"
    license = ["GPL-1.0-or-later", "LGPL-3.0-or-later", "GPL-2.0-or-later"]
    
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debuginfod": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_sqlite3": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debuginfod": False,
        "with_bzlib": True,
        "with_lzma": True,
        "with_sqlite3": False,
        "with_zlib": True,
    }

    generators = "pkg_config"

    _autotools = None
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler in ["Visual Studio", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration("Compiler %s not supported. "
                          "elfutils only supports gcc" % self.settings.compiler)
        if self.settings.compiler != "gcc":
            self.output.warn("Compiler %s is not gcc." % self.settings.compiler)

    def requirements(self):
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.31.1")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.6")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.4")
        if self.options.debuginfod:
            # FIXME: missing recipe for libmicrohttpd
            raise ConanInvalidConfiguration("libmicrohttpd is not available (yet) on CCI")

    def build_requirements(self):
        self.build_requires("automake/1.16.2")
        self.build_requires("m4/1.4.18")
        self.build_requires("flex/2.6.4")
        self.build_requires("bison/3.5.3")
        self.build_requires("pkgconf/1.7.3")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "elfutils" + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = [
                "--disable-werror",
                "--enable-static={}".format("no" if self.options.shared else "yes"),
                "--enable-deterministic-archives",
                "--enable-silent-rules",
                "--with-zlib" if self.options.with_zlib else "--without-zlib",
                "--with-bzlib" if self.options.with_bzlib else "--without-bzlib",
                "--with-lzma" if self.options.with_lzma else "--without-lzma",
                "--enable-debuginfod" if self.options.debuginfod else "--disable-debuginfod",
                'BUILD_STATIC={}'.format("0" if self.options.shared else "1"),
            ]
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv")
        autotools = self._configure_autotools()
        autotools.make()
    
    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.a")):
                os.remove(f)
        else:
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.so")):
                os.remove(f)
            for f in glob.glob(os.path.join(self.package_folder, "lib", "*.so.1")):
                os.remove(f)
        
    def package_info(self):
        # library components
        self.cpp_info.components["libelf"].libs = ["elf"]
        self.cpp_info.components["libelf"].requires = ["zlib::zlib"]

        self.cpp_info.components["libdw"].libs = ["dw"]
        self.cpp_info.components["libdw"].requires = ["libelf", "zlib::zlib", "bzip2::bzip2", "xz_utils::xz_utils"]

        self.cpp_info.components["libasm"].includedirs = ["include/elfutils"]
        self.cpp_info.components["libasm"].libs = ["asm"]
        self.cpp_info.components["libasm"].requires = ["libelf", "libdw"]

        # utilities
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        
        addr2line = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-addr2line" + bin_ext))
        self.output.info("Setting ADDR2LINE to {}".format(addr2line))
        self.env_info.ADDR2LINE = addr2line

        ar = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-ar" + bin_ext))
        self.output.info("Setting AR to {}".format(ar))
        self.env_info.AR = ar

        elfclassify = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-elfclassify" + bin_ext))
        self.output.info("Setting ELFCLASSIFY to {}".format(elfclassify))
        self.env_info.ELFCLASSIFY = elfclassify

        elfcmp = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-elfcmp" + bin_ext))
        self.output.info("Setting ELFCMP to {}".format(elfcmp))
        self.env_info.ELFCMP = elfcmp

        elfcompress = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-elfcompress" + bin_ext))
        self.output.info("Setting ELFCOMPRESS to {}".format(elfcompress))
        self.env_info.ELFCOMPRESS = elfcompress

        elflint = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-elflint" + bin_ext))
        self.output.info("Setting ELFLINT to {}".format(elflint))
        self.env_info.ELFLINT = elflint

        findtextrel = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-findtextrel" + bin_ext))
        self.output.info("Setting FINDTEXTREL to {}".format(findtextrel))
        self.env_info.FINDTEXTREL = findtextrel

        make_debug_archive = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-make-debug-archive" + bin_ext))
        self.output.info("Setting MAKE_DEBUG_ARCHIVE to {}".format(make_debug_archive))
        self.env_info.MAKE_DEBUG_ARCHIVE = make_debug_archive

        nm = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-nm" + bin_ext))
        self.output.info("Setting NM to {}".format(nm))
        self.env_info.NM = nm

        objdump = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-objdump" + bin_ext))
        self.output.info("Setting OBJDUMP to {}".format(objdump))
        self.env_info.OBJDUMP = objdump

        ranlib = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-ranlib" + bin_ext))
        self.output.info("Setting RANLIB to {}".format(ranlib))
        self.env_info.RANLIB = ranlib

        readelf = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-readelf" + bin_ext))
        self.output.info("Setting READELF to {}".format(readelf))
        self.env_info.READELF = readelf

        size = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-size" + bin_ext))
        self.output.info("Setting SIZE to {}".format(size))
        self.env_info.SIZE = size

        stack = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-stack" + bin_ext))
        self.output.info("Setting STACK to {}".format(stack))
        self.env_info.STACK = stack

        strings = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-strings" + bin_ext))
        self.output.info("Setting STRINGS to {}".format(strings))
        self.env_info.STRINGS = strings

        strip = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-strip" + bin_ext))
        self.output.info("Setting STRIP to {}".format(strip))
        self.env_info.STRIP = strip

        unstrip = tools.unix_path(os.path.join(self.package_folder, "bin", "eu-unstrip" + bin_ext))
        self.output.info("Setting UNSTRIP to {}".format(unstrip))
        self.env_info.UNSTRIP = unstrip

