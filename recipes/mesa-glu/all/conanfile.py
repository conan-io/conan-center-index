from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, load, rm, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


required_conan_version = ">=1.53.0"


class MesaGluConan(ConanFile):
    name = "mesa-glu"
    description = "Mesa's implementation of the OpenGL utility library"
    license = ("SGI-B-1.1", "SGI-B-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mesa3d.org/"
    topics = ("gl", "glu", "mesa", "opengl")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    provides = "glu"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _with_libglvnd(self):
        return self.settings.os in ["FreeBSD", "Linux"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # The glu headers include OpenGL headers.
        if self._with_libglvnd:
            self.requires("libglvnd/1.7.0", transitive_headers=True)

    def validate(self):
        if is_apple_os(self) or self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}")

    def build_requirements(self):
        self.tool_requires("meson/1.2.3")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["gl_provider"] = "glvnd" if self._with_libglvnd else "gl"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _extract_license(self):
        glu_header = load(self, os.path.join(self.source_folder, "include", "GL", "glu.h"))
        begin = glu_header.find("/*")
        end = glu_header.find("*/", begin)
        return glu_header[begin:end]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["GLU"]
        self.cpp_info.set_property("pkg_config_name", "glu")
