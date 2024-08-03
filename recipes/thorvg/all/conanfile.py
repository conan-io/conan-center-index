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
    topics = ("svg", "animation", "tvg")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_engines": ['sw', 'gl_beta', 'wg_beta', "gl"],
        "with_loaders": [False, 'tvg', 'svg', 'png', 'jpg', 'lottie', 'ttf', 'webp', 'all'],
        "with_savers": [False, 'tvg', 'gif', 'all'],
        "with_bindings": [False, 'capi', 'wasm_beta'],
        "with_tools": [False, 'svg2tvg', 'svg2png', 'lottie2gif', 'all'],
        "with_threads": [True, False],
        "with_vector": [True, False],  # removed in thorvg 0.13.1. Renamed to simd
        "with_simd": [True, False],  # legacy with_vector
        "with_examples": [True, False],
        "with_extra": [False, 'lottie_expressions'],
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
        "with_vector": False,
        "with_simd": False,
        "with_examples": False,
        "with_extra": 'lottie_expressions',
    }
    # See more here: https://github.com/thorvg/thorvg/blob/main/meson_options.txt
    options_description = {
        "with_engines": "Enable Rasterizer Engine in thorvg",
        "with_loaders": "Enable File Loaders in thorvg",
        "with_savers": "Enable File Savers in thorvg",
        "with_threads": "Enable the multi-threading task scheduler in thorvg",
        "with_vector": "Enable CPU Vectorization(SIMD) in thorvg (renamed in 0.13.1 to 'simd')",
        "with_simd": "Enable CPU Vectorization(SIMD) in thorvg",
        "with_bindings": "Enable API bindings",
        "with_tools": "Enable building thorvg tools",
        "with_examples": "Enable building examples",
        "with_extra": "Enable support for exceptionally advanced features",
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
        # Renamed to simd in higher versions
        if Version(self.version) > "0.13.0":
            del self.options.with_vector
        else:
            del self.options.with_simd
        if Version(self.version)  < "0.13.3":
            del self.options.with_extra

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

    def requirements(self):
        loaders_opt = str(self.options.with_loaders)
        if loaders_opt in ("all", "jpg"):
            self.requires("libjpeg-turbo/3.0.2")
        if loaders_opt in ("all", "png"):
            self.requires("libpng/1.6.43")
        if loaders_opt in ("all", "webp"):
            self.requires("libwebp/1.4.0")
        if self.settings.os == "Linux":
            if self.options.with_engines in ["gl", "gl_beta"]:
                self.requires("opengl/system")

    def build_requirements(self):
        self.tool_requires("meson/1.4.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

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
            "examples": bool(self.options.with_examples),
            "tests": False,
            "log": is_debug,
        })
        # Workaround to avoid: error D8016: '/O1' and '/RTC1' command-line options are incompatible
        if is_msvc(self) and is_debug:
            tc.project_options["optimization"] = "plain"
        # vector option renamed to simd
        if Version(self.version) > "0.13.0":
            tc.project_options["simd"] = bool(self.options.with_simd)
        else:
            tc.project_options["vector"] = bool(self.options.with_vector)
        if self.options.get_safe("with_extra") is not None:
            tc.project_options["extra"] = str(self.options.with_extra) if self.options.with_extra else ''
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        venv = VirtualBuildEnv(self)
        venv.generate()

    def _patch_sources(self):
        # Workaround to avoid: Stripping target 'src\\thorvg-0.dll'.
        if is_msvc(self) and self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), ", 'strip=true'", "")

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
        self.cpp_info.libs = ["thorvg"]

        self.cpp_info.set_property("pkg_config_name", "libthorvg")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
        if not self.options.shared:
            self.cpp_info.defines = ["TVG_STATIC"]
        else:
            self.cpp_info.defines = ["TVG_EXPORT", "TVG_BUILD"]
