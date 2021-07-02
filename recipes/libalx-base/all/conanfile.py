import os
from conans import ConanFile, tools


class libalx_base_conan(ConanFile):
    name = "libalx-base"
    description = "C/C++ library providing useful extensions"
    homepage = "https://github.com/alejandro-colomar/libalx"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.0-only"
    topics = ("conan", "libc")
    settings = "os", "compiler", "arch"
    requires = [
        ("libbsd/0.10.0"),
    ];
    no_copy_source = True

    @property
    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libalx-base is only available for GNU operating systems (e.g. Linux)")
        self._srcdir   = self.source_folder
        self._builddir = self.build_subfolder
        self._DESTDIR  = self.package_folder
        self._prefix   = ""

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        srcdir   = self._srcdir
        builddir = self._builddir
        self.run("make -C {} build-base builddir={}".format(srcdir, builddir))

    def package(self):
        srcdir   = self._srcdir
        builddir = self._builddir
        DESTDIR  = self._DESTDIR
        prefix   = self._prefix
        self.run("make -C {} install-base builddir={} DESTDIR={} prefix={}".format(
                          srcdir, builddir, DESTDIR, prefix))

    def package_info(self):
        pass

    def package_id(self):
        pass
