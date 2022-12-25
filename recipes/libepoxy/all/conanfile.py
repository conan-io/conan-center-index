from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build
from conans import  Meson, tools
import os
import glob

required_conan_version = ">=1.50.0"

class EpoxyConan(ConanFile):
    name = "libepoxy"
    description = "libepoxy is a library for handling OpenGL function pointer management"
    topics = ("libepoxy", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/anholt/libepoxy"
    license = "MIT"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "glx": [True, False],
        "egl": [True, False],
        "x11": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "glx": True,
        "egl": True,
        "x11": True
    }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Windows":
            if not self.options.shared:
                raise ConanInvalidConfiguration("Static builds on Windows are not supported")
        if hasattr(self, "settings_build") and build.cross_building(self):
            raise ConanInvalidConfiguration("meson build helper cannot cross-compile. It has to be migrated to conan.tools.meson")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.shared = True
        if self.settings.os != "Linux":
            del self.options.glx
            del self.options.egl
            del self.options.x11

    def build_requirements(self):
        self.build_requires("meson/0.63.1")

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            if self.options.x11:
                self.requires("xorg/system")
            if self.options.egl:
                self.requires("egl/system")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        defs = {}
        defs["docs"] = "false"
        defs["tests"] = "false"
        for opt in ["glx", "egl"]:
            defs[opt] = "yes" if self.options.get_safe(opt, False) else "no"
        for opt in ["x11"]:
            defs[opt] = "true" if self.options.get_safe(opt, False) else "false"
        args=[]
        args.append("--wrap-mode=nofallback")
        self._meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=[self.install_folder], args=args)
        return self._meson

    def build(self):
        files.apply_conandata_patches(self)
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

    def package_info(self):
        self.cpp_info.libs = ["epoxy"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
        self.cpp_info.names["pkg_config"] = "epoxy"

        pkgconfig_variables = {
            'epoxy_has_glx': '1' if self.options.get_safe("glx") else '0',
            'epoxy_has_egl': '1' if self.options.get_safe("egl") else '0',
            'epoxy_has_wgl': '1' if self.settings.os == "Windows" else '0',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))
