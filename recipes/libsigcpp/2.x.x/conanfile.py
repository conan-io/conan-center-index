import os

from conans import ConanFile, Meson, tools


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    description = (
        "libsigc++ implements a typesafe callback system for standard C++."
    )
    topics = ("conan", "libsigcpp", "callback")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libsigc++-{}".format(self.version), self._source_subfolder)
        tools.replace_in_file(
            os.path.join(
                self.source_folder, self._source_subfolder, "meson.build"
            ),
            "subdir('tests')",
            "",
        )

    def _configure_build(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)

        args = [
            "-Dmaintainer-mode=false",
            "-Ddist-warnings=no",
            "-Ddist-warnings=no",
            "-Dbuild-deprecated-api=true",
            "-Dbuild-documentation=false",
            "-Dvalidation=false",
            "-Dbuild-pdf=false",
            "-Dbuild-examples=false",
            "-Dbenchmark=false",
        ]

        self._meson.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder,
            args=args,
        )
        return self._meson

    def build(self):
        meson = self._configure_build()
        meson.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_build()
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = [
            "include/sigc++-2.0",
            "lib/sigc++-2.0/include",
        ]
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.names["pkg_config"] = "sigc++-2.0"
