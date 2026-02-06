import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, rename, replace_in_file, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.64.0 <2 || >=2.2.0"


class ThorvgConan(ConanFile):
    name = "thorvg"
    description = "ThorVG is a platform-independent portable library that allows for drawing vector-based scenes and animations."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/thorvg/thorvg"
    topics = ("svg", "lottie", "animation", "graphics", "rendering")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_engines": ['sw', 'gl_beta', 'wg_beta', "gl", "wg", "all"],
        "with_loaders": [False, 'tvg', 'svg', 'png', 'jpg', 'lottie', 'ttf', 'webp', 'all'],
        "with_savers": [False, 'tvg', 'gif', 'all'],
        "with_bindings": [False, 'capi', 'wasm_beta'],
        "with_tools": [False, 'svg2tvg', 'svg2png', 'lottie2gif', 'all'],
        "with_threads": [True, False],
        "with_simd": [True, False],
        "with_examples": [True, False],
        "with_lottie_exp": [False, True],
        "with_openmp": [False, True],
        "with_gl_variant": [False, True],
        "with_file": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_engines": 'sw',
        "with_loaders": 'all',
        "with_savers": False,
        "with_bindings": 'capi',
        "with_tools": False,
        "with_threads": True,
        "with_simd": False,
        "with_examples": False,
        "with_lottie_exp": True,
        "with_openmp": False,
        "with_gl_variant": False,
        "with_file": True,
    }
    # See more here: https://github.com/thorvg/thorvg/blob/main/meson_options.txt
    options_description = {
        "with_engines": "Enable Rasterizer Engine in thorvg",
        "with_loaders": "Enable File Loaders in thorvg",
        "with_savers": "Enable File Savers in thorvg",
        "with_threads": "Enable the multi-threading task scheduler in thorvg",
        "with_simd": "Enable CPU Vectorization(SIMD) in thorvg",
        "with_bindings": "Enable API bindings",
        "with_tools": "Enable building thorvg tools",
        "with_examples": "Enable building examples",
        "with_lottie_exp": "Enable support for Lottie Expressions",
        "with_openmp": "Enable support for OpenMP",
        "with_gl_variant": "Enable support for OpenGL Variant",
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.15.6":
            del self.options.with_file

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_msvc(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(
                f"{self.ref} doesn't support debug build on MSVC."
            )

        if Version(self.version) < "0.14.0" and self.options.with_engines in ["gl"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_engines=gl, use with_engines=gl_beta instead")
        if Version(self.version) >= "0.14.0" and self.options.with_engines in ["gl_beta"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_engines=gl_beta, use with_engines=gl instead")
        if Version(self.version) < "1.0.0" and self.options.with_engines in ["wg"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_engines=wg, use with_engines=wg_beta instead")
        if Version(self.version) >= "1.0.0" and self.options.with_engines in ["wg_beta"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_engines=wg_beta, use with_engines=wg instead")
        if Version(self.version) < "1.0.0" and self.options.with_engines in ["all"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_engines=all")
        if Version(self.version) >= "1.0.0" and self.options.with_loaders in ["tvg"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_loaders=tvg")
        if Version(self.version) >= "1.0.0" and self.options.with_savers in ["tvg"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_savers=tvg")
        if Version(self.version) >= "1.0.0" and self.options.with_bindings in ["wasm_beta"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_bindings=wasm_beta")
        if Version(self.version) >= "1.0.0" and self.options.with_tools in ["svg2tvg"]:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_tools=svg2tvg")
        if Version(self.version) < "1.0.0" and self.options.with_openmp is True:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_openmp=True")
        if Version(self.version) < "1.0.0" and self.options.with_gl_variant is True:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support with_gl_variant=True")

    def requirements(self):
        loaders_opt = str(self.options.with_loaders)
        if loaders_opt in ("all", "jpg"):
            self.requires("libjpeg-turbo/[>=3.0.2 <4]")
        if loaders_opt in ("all", "png"):
            self.requires("libpng/[>=1.6.43 <2]")
        if loaders_opt in ("all", "webp"):
            self.requires("libwebp/[>=1.4.0 <2]")
        if self.settings.os == "Linux":
            if self.options.with_engines in ["gl", "gl_beta"]:
                self.requires("opengl/system")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self, backend=("vs" if is_msvc(self) else None))
        is_debug = self.settings.get_safe("build_type") == "Debug"
        tc.project_options.update({
            "engines": str(self.options.with_engines),
            "loaders": str(self.options.with_loaders) if self.options.with_loaders else '',
            "savers": str(self.options.with_savers) if self.options.with_savers else '',
            "bindings": str(self.options.with_bindings) if self.options.with_bindings else '',
            "tools": str(self.options.with_tools )if self.options.with_tools else '',
            "threads": bool(self.options.with_threads),
            "tests": False,
            "log": is_debug,
        })
        # Workaround to avoid: error D8016: '/O1' and '/RTC1' command-line options are incompatible
        if is_msvc(self) and is_debug:
            tc.project_options["optimization"] = "plain"
        tc.project_options["simd"] = bool(self.options.with_simd)
        extras = []
        if self.options.with_lottie_exp:
            if Version(self.version) < "1.0.0":
                extras.append("lottie_expressions")
            else:
                extras.append("lottie_exp")
        if self.options.with_openmp:
            extras.append("openmp")
        if self.options.with_gl_variant:
            extras.append("gl_variant")
        if extras:
            tc.project_options["extra"] = ",".join(extras)
        if "with_file" in self.options:
            tc.project_options["file"] = self.options.with_file
        if Version(self.version) < "1.0.0":
            tc.project_options["examples"] = bool(self.options.with_examples)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        venv = VirtualBuildEnv(self)
        venv.generate()

    def _patch_sources(self):
        # Workaround to avoid: Stripping target 'src\\thorvg-0.dll'.
        if is_msvc(self) and self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), ", 'strip=true'", "")

        if Version(self.version) >= "0.15.1" and Version(self.version) < "1.0.0" and self.options.with_threads:
            # As OpenMP is tagged as "required: false", let's disable it for now to avoid extra flags and requirements injections.
            # Notice that the use of disabler() is not working here. If it's used, there is no targets to build.
            replace_in_file(self, os.path.join(self.source_folder, "src", "renderer", "sw_engine", "meson.build"),
                            "omp_dep = dependency('openmp', required: false)",
                            "omp_dep = []")
            replace_in_file(self, os.path.join(self.source_folder, "src", "renderer", "sw_engine", "meson.build"),
                            "omp_dep.found()",
                            "false")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

        if is_msvc(self) and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "libthorvg.a"), os.path.join(self.package_folder, "lib", "thorvg.lib"))

    def package_info(self):
        if Version(self.version) >= "1.0.0":
            self.cpp_info.libs = ["thorvg-1"]
        else:
            self.cpp_info.libs = ["thorvg"]

        self.cpp_info.set_property("pkg_config_name", "libthorvg")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
        if not self.options.shared:
            self.cpp_info.defines = ["TVG_STATIC"]
        else:
            self.cpp_info.defines = ["TVG_EXPORT", "TVG_BUILD"]
