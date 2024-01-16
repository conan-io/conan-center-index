import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, load, replace_in_file, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"


class MesaDemosConan(ConanFile):
    name = "mesa-demos"
    package_type = "application"
    description = "The Mesa Demos package contains a large number of OpenGL demonstration and test programs."
    topics = ("demo", "egl", "gl", "gles", "graphics", "mesa", "opengl", "vulkan", "wayland", "x11")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/mesa/demos"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "egl": [True, False],
        "gles1": [True, False],
        "gles2": [True, False],
        "glut": [True, False],
        "with_freeglut": [True, False],
        "with_libdrm": [True, False],
        "with_system_data_files": [True, False],
        "with_vulkan": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "egl": True,
        "gles1": True,
        "gles2": True,
        "glut": True,
        "with_freeglut": True,
        "with_libdrm": True,
        "with_system_data_files": False,
        "with_vulkan": True,
        "with_wayland": True,
        "with_x11": True,
    }

    @property
    def _has_build_profile(self):
        return hasattr(self, "settings_build")

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "13",
            "clang": "5",
            "gcc": "8",
            "msvc": "192",
            "Visual Studio": "16",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if is_apple_os(self):
            self.options.rm_safe("with_freeglut")
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if self.settings.os != "Linux":
            self.options.rm_safe("with_wayland")
        if self.settings.os not in ["FreeBSD", "Linux"]:
            self.options.rm_safe("with_libdrm")

    def configure(self):
        if self.options.get_safe("egl"):
            self.options["libglvnd"].egl = True
        if self.options.get_safe("gles1"):
            self.options["libglvnd"].gles1 = True
        if self.options.get_safe("gles2"):
            self.options["libglvnd"].gles2 = True
        if self.options.get_safe("gles1") or self.options.get_safe("gles2"):
            self.options["freeglut"].gles = True
        if self.options.get_safe("with_glut") and self.options.get_safe("with_wayland"):
            self.options["freeglut"].with_wayland = True
        if self.options.get_safe("with_x11"):
            self.options["libglvnd"].glx = True
            self.options["xkbcommon"].with_x11 = True
        if self.options.get_safe("with_wayland"):
            self.options["xkbcommon"].with_wayland = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if is_apple_os(self) or self.settings.os == "Windows":
            self.requires("glu/system")
        else:
            self.requires("mesa-glu/9.0.3")

        if self.settings.os in ["FreeBSD", "Linux"]:
            self.requires("libglvnd/1.7.0")

        if self.options.get_safe("with_freeglut"):
            self.requires("freeglut/3.4.0")

        if self.options.get_safe("with_libdrm"):
            self.requires("libdrm/2.4.119")

        if self.options.get_safe("with_vulkan"):
            self.requires("vulkan-loader/1.3.268.0")

        if self.options.get_safe("with_wayland"):
            self.requires("libdecor/0.2.2")

            # Override requirements for libdecor's use of Pango.
            # todo Remove these when a PR to update Pango finally gets merged.
            self.requires("freetype/2.13.2")
            self.requires("fontconfig/2.14.2")
            self.requires("glib/2.78.1")

            self.requires("wayland/1.22.0")
            self.requires("wayland-protocols/1.32")

        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

        if self.options.get_safe("with_x11") or self.options.get_safe("with_wayland"):
            self.requires("xkbcommon/1.6.0")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least version {minimum_version} of {self.settings.compiler}"
            )

        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.get_safe("egl") and not self.dependencies["libglvnd"].options.egl:
                raise ConanInvalidConfiguration(f"{self.ref} requires the egl option of libglvnd to be enabled when the egl option is enabled")
            if self.options.get_safe("gles1") and not self.dependencies["libglvnd"].options.gles1:
                raise ConanInvalidConfiguration(f"{self.ref} requires the gles1 option of libglvnd to be enabled when the gles1 option is enabled")
            if self.options.get_safe("gles2") and not self.dependencies["libglvnd"].options.gles2:
                raise ConanInvalidConfiguration(f"{self.ref} requires the gles2 option of libglvnd to be enabled when the gles1 option is enabled")
            if self.options.get_safe("with_x11") and not self.dependencies["libglvnd"].options.glx:
                raise ConanInvalidConfiguration(f"{self.ref} requires the glx option of libglvnd to be enabled when the gles option is disabled")
        if self.options.get_safe("with_wayland") and not self.dependencies["xkbcommon"].options.with_wayland:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_wayland option of xkbcommon to be enabled when the with_wayland option is enabled")
        if self.options.get_safe("with_x11") and not self.dependencies["xkbcommon"].options.with_x11:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_x11 option of xkbcommon to be enabled when the with_x11 option is enabled")

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/<host_version>")
        if self.options.get_safe("with_vulkan"):
            self.tool_requires("glslang/11.7.0")

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "meson.build"),
            "  subdir('demos')",
            "  # subdir('demos')",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "meson.build"),
            "  subdir('tests')",
            "  # subdir('tests')",
        )
        if self.options.get_safe("with_wayland"):
            meson_build_file = os.path.join(self.source_folder, "meson.build")
            if self._has_build_profile:
                replace_in_file(
                    self,
                    meson_build_file,
                    "dep_wl_scanner = dependency('wayland-scanner', native: true)",
                    "dep_wl_scanner = dependency('wayland-scanner_BUILD', native: true)",
                )
            else:
                replace_in_file(
                    self,
                    meson_build_file,
                    "dep_wl_scanner = dependency('wayland-scanner', native: true)",
                    "# dep_wl_scanner = dependency('wayland-scanner', native: true)",
                )
                replace_in_file(
                    self,
                    meson_build_file,
                    "prog_wl_scanner = find_program(dep_wl_scanner..get_variable(pkgconfig : 'wayland_scanner'))",
                    "prog_wl_scanner = find_program('wayland-scanner')",
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        boolean = lambda option: self.options.get_safe(option, default=False)
        feature = (
            lambda option: "enabled" if self.options.get_safe(option) else "disabled"
        )

        tc = MesonToolchain(self)
        tc.project_options["datadir"] = "res"
        tc.project_options["egl"] = feature("egl")
        tc.project_options["gles1"] = feature("gles1")
        tc.project_options["gles2"] = feature("gles2")
        tc.project_options["glut"] = feature("with_glut")
        tc.project_options["libdrm"] = feature("with_libdrm")
        tc.project_options["osmesa"] = feature("osmesa")
        tc.project_options["vulkan"] = feature("with_vulkan")
        tc.project_options["wayland"] = feature("with_wayland")
        tc.project_options["with-system-data-files"] = boolean("with_system_data_files")
        tc.project_options["x11"] = feature("with_x11")
        if self._has_build_profile:
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        if self._has_build_profile and self.options.get_safe("with_wayland"):
            pkg_config_deps.build_context_activated = ["wayland"]
            pkg_config_deps.build_context_suffix = {"wayland": "_BUILD"}
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _extract_license(self):
        vkgears_header = load(self, os.path.join(self.source_folder, "src", "vulkan", "vkgears.c"))
        begin = vkgears_header.find("Copyright")
        end = vkgears_header.find("*/", begin)
        return vkgears_header[begin:end]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
