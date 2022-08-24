import os
from conan import ConanFile
from conan.tools.files import rename, get
from conans import Meson, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class Dav1dConan(ConanFile):
    name = "dav1d"
    description = "dav1d is a new AV1 cross-platform decoder, open-source, and focused on speed, size and correctness."
    homepage = "https://www.videolan.org/projects/dav1d.html"
    topics = ("av1", "codec", "video", "decoding")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_depth": ["all", 8, 16],
        "with_tools": [True, False],
        "assembly": [True, False],
        "with_avx512": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_depth": "all",
        "with_tools": True,
        "assembly": True,
        "with_avx512": False
    }
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

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
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            # debug builds with assembly often causes linker hangs or LNK1000
            self.options.assembly = False
        if tools.Version(self.version) < "1.0.0":
            del self.options.with_avx512

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.assembly:
            del self.options.with_avx512
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        # Meson versions since 0.51.0 do not work with autodetect symbol prefix
        # so the nasm build is broken
        # See upstream bug https://github.com/mesonbuild/meson/issues/5482
        self.build_requires("meson/0.51.0")
        if self.options.assembly:
            self.build_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "meson.build"),
                              "subdir('doc')", "")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["enable_tests"] = False
        self._meson.options["enable_asm"] = self.options.assembly
        if tools.Version(self.version) < "1.0.0":
            self._meson.options["enable_avx512"] = self.options.get_safe("with_avx512", False)
        self._meson.options["enable_tools"] = self.options.with_tools
        if self.options.bit_depth == "all":
            self._meson.options["bitdepths"] = "8,16"
        else:
            self._meson.options["bitdepths"] = str(self.options.bit_depth)
        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder, pkg_config_paths=[self.install_folder])
        return self._meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pdb")

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            # https://github.com/mesonbuild/meson/issues/7378
            rename(self,
                   os.path.join(self.package_folder, "lib", "libdav1d.a"),
                   os.path.join(self.package_folder, "lib", "dav1d.lib"))

    def package_info(self):
        self.cpp_info.libs = ["dav1d"]
        self.cpp_info.names["pkg_config"] = "dav1d"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
