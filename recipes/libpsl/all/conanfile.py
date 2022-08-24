from conans import ConanFile, Meson, tools
import os

required_conan_version = ">=1.29.1"

class LibPslConan(ConanFile):
    name = "libpsl"
    description = "C library for the Public Suffix List"
    homepage = "https://github.com/rockdaboot/libpsl"
    topics = ("conan", "psl", "suffix", "TLD", "gTLD", ".com", ".net")
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_idna": [False, "icu", "libidn", "libidn2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_idna": "icu",
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    generators = "pkg_config"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("meson/0.55.3")
        self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        if self.options.with_idna == "icu":
            self.requires("icu/68.1")
        elif self.options.with_idna == "libidn":
            self.requires("libidn/1.36")
        elif self.options.with_idna == "libidn2":
            self.requires("libidn2/2.3.0")
        if self.options.with_idna in ("libidn", "libidn2"):
            self.requires("libunistring/0.9.10")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("libpsl-{}".format(self.version), self._source_subfolder)

    @property
    def _idna_option(self):
        return {
            "False": "no",
            "icu": "libicu",
        }.get(str(self.options.with_idna), str(self.options.with_idna))

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["runtime"] = self._idna_option
        self._meson.options["builtin"] = self._idna_option
        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder, pkg_config_paths=[self.install_folder])
        return self._meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        if not self.options.shared and self.settings.compiler == "Visual Studio":
            os.rename(os.path.join(self.package_folder, "lib", "libpsl.a"),
                      os.path.join(self.package_folder, "lib", "psl.lib"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["psl"]
        self.cpp_info.names["pkg_config"] = "libpsl"
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        if not self.options.shared:
            self.cpp_info.defines = ["PSL_STATIC"]
