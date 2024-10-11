import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"


class Imlib2Conan(ConanFile):
    name = "imlib2"
    description = "Image loading and rendering library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://docs.enlightenment.org/api/imlib2/html/"
    topics = ("image", "image-processing",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_text": [True, False],
        "with_bz2": [True, False],
        "with_gif": [True, False],
        "with_heif": [True, False],
        "with_id3": [True, False],
        "with_j2k": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_jxl": [True, False],
        "with_lzma": [True, False],
        "with_png": [True, False],
        "with_raw": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_x": [True, False],
        "with_y4m": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_text": False,
        "with_bz2": False,
        "with_gif": True,
        "with_heif": False,
        "with_id3": False,
        "with_j2k": False,
        "with_jpeg": "libjpeg",
        "with_jxl": False,
        "with_lzma": False,
        "with_png": True,
        "with_raw": False,
        "with_tiff": True,
        "with_webp": False,
        "with_x": False,
        "with_y4m": False,
        "with_zlib": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_text:
            self.requires("freetype/2.13.2")
        if self.options.with_bz2:
            self.requires("bzip2/1.0.8")
        if self.options.with_gif:
            self.requires("giflib/5.2.2")
        if self.options.with_heif:
            self.requires("libheif/1.18.2")
        if self.options.with_id3:
            self.requires("libid3tag/0.15.1b")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.with_j2k:
            self.requires("openjpeg/2.5.2")
        if self.options.with_jxl:
            self.requires("libjxl/0.10.3")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_raw:
            self.requires("libraw/0.21.2")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.get_safe("with_x"):
            # Only xorg::x11 is used.
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_y4m:
            self.requires("libyuv/1892")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        # if self.options.with_ps:
        #     self.requires("libspectre/0.2.12")
        # if self.options.with_svg:
        #     self.requires("librsvg/2.57.0")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-mmx={yes_no(self.settings.arch in ['x86', 'x86_64'])}",
            f"--enable-amd64={yes_no( self.settings.arch == 'x86_64')}",
            f"--enable-text={yes_no(self.options.enable_text)}",
            f"--with-bz2={yes_no(self.options.with_bz2)}",
            f"--with-gif={yes_no(self.options.with_gif)}",
            f"--with-heif={yes_no(self.options.with_heif)}",
            f"--with-id3={yes_no(self.options.with_id3)}",
            f"--with-j2k={yes_no(self.options.with_j2k)}",
            f"--with-jpeg={yes_no(self.options.with_jpeg)}",
            f"--with-jxl={yes_no(self.options.with_jxl)}",
            f"--with-lzma={yes_no(self.options.with_lzma)}",
            f"--with-png={yes_no(self.options.with_png)}",
            f"--with-raw={yes_no(self.options.with_raw)}",
            f"--with-tiff={yes_no(self.options.with_tiff)}",
            f"--with-webp={yes_no(self.options.with_webp)}",
            f"--with-x={yes_no(self.options.get_safe('with_x'))}",
            f"--with-y4m={yes_no(self.options.with_y4m)}",
            f"--with-zlib={yes_no(self.options.with_zlib)}",
            "--with-ps=no",
            "--with-svg=no",
        ])
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "imlib2")
        self.cpp_info.libs = ["Imlib2"]
        self.cpp_info.resdirs = ["res"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
