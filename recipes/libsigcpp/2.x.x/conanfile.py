import os

from conans.errors import ConanInvalidConfiguration
from conans import ConanFile, Meson, tools

required_conan_version = ">=1.29.0"

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

    def build_requirements(self):
        self.build_requires("meson/0.56.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            self.options.shared = True

    def configure(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if (
            not self.options.shared
            and compiler == "Visual Studio"
            and version <= "16"
        ):
            raise ConanInvalidConfiguration(
                "{} {} is not supported for static compilation".format(
                    compiler,
                    version,
                )
            )

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
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.includedirs = [
            "include/sigc++-2.0",
            "lib/sigc++-2.0/include",
        ]
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.names["pkg_config"] = "sigc++-2.0"
