from conans import tools, ConanFile, Meson
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class FriBiDiCOnan(ConanFile):
    name = "fribidi"
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    topics = ("conan", "fribidi", "unicode", "bidirectional", "text")
    license = "LGPL-2.1"
    homepage = "https://github.com/fribidi/fribidi"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_deprecated": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_deprecated": True,
    }
    exports_sources = "patches/**"

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

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def build_requirements(self):
        self.build_requires("meson/0.59.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["deprecated"] = self.options.with_deprecated
        self._meson.options["docs"] = False
        if tools.Version(self.version) >= "1.0.10":
            self._meson.options["bin"] = False
            self._meson.options["tests"] = False
        self._meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._meson

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        if self.settings.compiler == "Visual Studio":
            lib_a = os.path.join(self.package_folder, "lib", "libfribidi.a")
            if os.path.isfile(lib_a):
                tools.rename(lib_a, os.path.join(self.package_folder, "lib", "fribidi.lib"))
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.pdb")

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["fribidi"]
        self.cpp_info.includedirs.append(os.path.join("include", "fribidi"))
        if not self.options.shared:
            if tools.Version(self.version) >= "1.0.10":
                self.cpp_info.defines.append("FRIBIDI_LIB_STATIC")
            else:
                self.cpp_info.defines.append("FRIBIDI_STATIC")

        self.cpp_info.names["pkg_config"] = "fribidi"
