import glob
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, msvs_toolset
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, "
        "converting, and editing raster image and vector image files"
    )
    license = "ImageMagick"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    topics = ("images", "manipulating")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hdri": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "with_djvu": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_zlib": True,
        "with_bzlib": True,
        "with_lzma": True,
        "with_lcms": True,
        "with_openexr": False, # FIXME
        "with_heic": False, # FIXME
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_openjp2": False,  # FIXME
        "with_pango": False,  # FIXME
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_djvu": False,
        "utilities": True,
    }

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
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.2")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
        if self.options.with_openexr:
            self.requires("openexr/3.1.7")
        if self.options.with_heic:
            self.requires("libheif/1.13.0")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.0")
        if self.options.with_pango:
            self.requires("pango/1.50.10")
        if self.options.with_png:
            self.requires("libpng/1.6.39")
        if self.options.with_tiff:
            self.requires("libtiff/4.5.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.0")
        if self.options.with_xml2:
            self.requires("libxml2/2.11.4")
        if self.options.with_freetype:
            self.requires("freetype/2.13.0")
        if self.options.with_djvu:
            # FIXME: missing djvu recipe
            self.output.warning(
                "There is no djvu package available on Conan (yet). "
                "This recipe will use the one present on the system (if available)."
            )

    @property
    def _modules(self):
        return ["Magick++", "MagickWand", "MagickCore"]

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds of ImageMagick require MFC which cannot currently be sourced from CCI."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

        if self.info.settings.os == "Windows":
            visualmagick_version = list(self.conan_data["sources"][self.version]["visualmagick"].keys())[0]
            get(
                self,
                **self.conan_data["sources"][self.version]["visualmagick"][visualmagick_version],
                destination="VisualMagick",
                strip_root=True,
            )

    @property
    def _msvc_runtime_suffix(self):
        return {
            "MT": "StaticMT",
            "MTd": "StaticMTD",
            "MD": "DynamicMT",
            "MDd": "DynamicMT",
        }.get(str(self.settings.compiler.runtime))

    @property
    def _visual_studio_version(self):
        return {
            9: "/VS2002",
            10: "/VS2010",
            11: "/VS2012",
            12: "/VS2013",
            14: "/VS2015",
            15: "/VS2017",
            16: "/VS2019",
            17: "/VS2022",
        }.get(int(str(self.settings.compiler.version)))

    @property
    def _msvc_runtime_flag(self):
        return {
            "MT": "/smt",
            "MTd": "/smtd",
            "MD": "/dmt",
            "MDd": "/mdt",
        }.get(str(self.settings.compiler.runtime))

    def _generate_msvc(self):
        with chdir(self, os.path.join("VisualMagick", "configure")):
            tc = MSBuildToolchain(self)
            # fatal error C1189: #error:  Please use the /MD switch for _AFXDLL builds
            tc.cxxflags = ["/MD"]
            tc.project_file = "configure.vcxproj"
            tc.platforms = {"x86": "Win32"}
            tc.force_vcvars = True

            # https://github.com/ImageMagick/ImageMagick-Windows/blob/master/AppVeyor/Build.ps1
            configure_args = ["/noWizard"]
            configure_args.append(self._msvc_runtime_flag)
            configure_args.append(self._visual_studio_version)
            configure_args.append("/hdri" if self.options.hdri else "/noHdri")
            configure_args.append(f"/Q{self.options.quantum_depth}")
            if self.settings.arch == "x86_64":
                configure_args.append("/x64")
            save(self, "configure_args", " ".join(configure_args))

        suffix = self._msvc_runtime_suffix
        for module in self._modules:
            with chdir(self, os.path.join("VisualMagick", module)):
                tc = MSBuildToolchain(self)
                tc.project_file = f"CORE_{module}_{suffix}.vcxproj"
                tc.upgrade_project = False
                tc.platforms = {
                    "x86": "Win32",
                    "x86_64": "x64",
                }

        with chdir(self, os.path.join("VisualMagick", "coders")):
            pattern = f"IM_MOD_*_{suffix}.vcxproj" if self.options.shared else f"CORE_coders_{suffix}.vcxproj"
            projects = glob.glob(pattern)
            for project in projects:
                tc = MSBuildToolchain(self)
                tc.project_file = project
                tc.upgrade_project = False
                tc.platforms = {
                    "x86": "Win32",
                    "x86_64": "x64",
                }

    def _generate_autotools(self):
        def yes_no(o):
            return "yes" if o else "no"

        tc = AutotoolsToolchain(self)
        tc.configure_args = [
            "--prefix=/",
            "--disable-openmp",
            "--disable-docs",
            "--with-perl=no",
            "--with-x=no",
            "--with-fontconfig=no",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-hdri={}".format(yes_no(self.options.hdri)),
            "--with-quantum-depth={}".format(self.options.quantum_depth),
            "--with-zlib={}".format(yes_no(self.options.with_zlib)),
            "--with-bzlib={}".format(yes_no(self.options.with_bzlib)),
            "--with-lzma={}".format(yes_no(self.options.with_lzma)),
            "--with-lcms={}".format(yes_no(self.options.with_lcms)),
            "--with-openexr={}".format(yes_no(self.options.with_openexr)),
            "--with-heic={}".format(yes_no(self.options.with_heic)),
            "--with-jbig={}".format(yes_no(self.options.with_jbig)),
            "--with-jpeg={}".format(yes_no(self.options.with_jpeg)),
            "--with-openjp2={}".format(yes_no(self.options.with_openjp2)),
            "--with-pango={}".format(yes_no(self.options.with_pango)),
            "--with-png={}".format(yes_no(self.options.with_png)),
            "--with-tiff={}".format(yes_no(self.options.with_tiff)),
            "--with-webp={}".format(yes_no(self.options.with_webp)),
            "--with-xml={}".format(yes_no(self.options.with_xml2)),
            "--with-freetype={}".format(yes_no(self.options.with_freetype)),
            "--with-djvu={}".format(yes_no(self.options.with_djvu)),
            "--with-utilities={}".format(yes_no(self.options.utilities)),
        ]
        tc.generate()

        tc = AutotoolsDeps(self)
        # FIXME: workaround for xorg/system adding system includes https://github.com/conan-io/conan-center-index/issues/6880
        # if "/usr/include/uuid" in tc.include_paths:
        #     tc.include_paths.remove("/usr/include/uuid")
        tc.generate()

    def generate(self):
        if is_msvc(self):
            self._generate_msvc()
        else:
            self._generate_autotools()

    def _patch_sources_msvc(self):
        apply_conandata_patches(self)
        # FIXME: package LiquidRescale  aka liblqr
        replace_in_file(self, os.path.join("VisualMagick", "lqr", "Config.txt"), "#define MAGICKCORE_LQR_DELEGATE", "")
        # FIXME: package LibRaw
        replace_in_file(
            self,
            os.path.join("VisualMagick", "libraw", "Config.txt"),
            "#define MAGICKCORE_RAW_R_DELEGATE",
            "",
        )
        # FIXME: package FLIF (FLIF: Free Lossless Image Format)
        replace_in_file(
            self, os.path.join("VisualMagick", "flif", "Config.txt"), "#define MAGICKCORE_FLIF_DELEGATE", ""
        )
        # FIXME: package librsvg
        replace_in_file(
            self, os.path.join("VisualMagick", "librsvg", "Config.txt"), "#define MAGICKCORE_RSVG_DELEGATE", ""
        )
        if not self.options.shared:
            for module in self._modules:
                replace_in_file(self, os.path.join("VisualMagick", module, "Config.txt"), "[DLL]", "[STATIC]")
            replace_in_file(
                self,
                os.path.join("VisualMagick", "coders", "Config.txt"),
                "[DLLMODULE]",
                "[STATIC]\n[DEFINES]\n_MAGICKLIB_",
            )

        if self.settings.arch == "x86_64":
            project = os.path.join("VisualMagick", "configure", "configure.vcxproj")
            replace_in_file(self, project, "Win32", "x64")
            replace_in_file(self, project, "/MACHINE:I386", "/MACHINE:x64")

        with chdir(self, os.path.join("VisualMagick", "configure")):
            toolset = msvs_toolset(self)
            replace_in_file(
                self,
                "configure.vcxproj",
                "<PlatformToolset>v120</PlatformToolset>",
                f"<PlatformToolset>{toolset}</PlatformToolset>",
            )

        # GdiPlus requires C++, but ImageMagick has *.c files
        suffix = self._msvc_runtime_suffix
        project = f"IM_MOD_emf_{suffix}.vcxproj" if self.options.shared else f"CORE_coders_{suffix}.vcxproj"
        replace_in_file(
            self,
            os.path.join("VisualMagick", "coders", project),
            '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">',
            '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">\n<CompileAs>CompileAsCpp</CompileAs>',
        )

        # disable incorrectly detected OpenCL
        baseconfig = os.path.join(self.source_folder, "MagickCore", "magick-baseconfig.h")
        replace_in_file(self, baseconfig, "#define MAGICKCORE__OPENCL", "#undef MAGICKCORE__OPENCL", strict=False)
        replace_in_file(
            self,
            baseconfig,
            "#define MAGICKCORE_HAVE_CL_CL_H",
            "#undef MAGICKCORE_HAVE_CL_CL_H",
            strict=False,
        )

    def _build_msvc(self):
        self._patch_sources_msvc()

        with chdir(self, os.path.join("VisualMagick", "configure")):
            msbuild = MSBuild(self)
            msbuild.build("configure.vcxproj")
            configure_args = load(self, "configure_args")
            self.run(f"configure.exe {configure_args}")

        suffix = self._msvc_runtime_suffix
        for module in self._modules:
            with chdir(self, os.path.join("VisualMagick", module)):
                msbuild = MSBuild(self)
                msbuild.build(f"CORE_{module}_{suffix}.vcxproj")

        with chdir(self, os.path.join("VisualMagick", "coders")):
            pattern = f"IM_MOD_*_{suffix}.vcxproj" if self.options.shared else f"CORE_coders_{suffix}.vcxproj"
            projects = glob.glob(pattern)
            for project in projects:
                msbuild = MSBuild(self)
                msbuild.build(project)

    def _build_autotools(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def build(self):
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            for pattern in ["*CORE_*.lib", "*CORE_*.dll", "*IM_MOD_*.dll"]:
                copy(
                    self,
                    pattern=pattern,
                    dst=os.path.join(self.package_folder, "lib"),
                    src=os.path.join("VisualMagick", "lib"),
                    keep_path=False,
                )
            for module in self._modules:
                copy(
                    self,
                    pattern="*.h",
                    dst=os.path.join("include", f"ImageMagick-{Version(self.version).major}", module),
                    src=os.path.join(self.source_folder, module),
                )
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            with chdir(self, self.package_folder):
                # remove undesired files
                rmdir(self, os.path.join("lib", "pkgconfig"))  # pc files
                rmdir(self, "etc")
                rmdir(self, "share")
                rm(self, "*.la", "lib", recursive=True)

    def _libname(self, library):
        if is_msvc(self):
            infix = "DB" if self.settings.build_type == "Debug" else "RL"
            return f"CORE_{infix}_{library}_"
        else:
            suffix = "HDRI" if self.options.hdri else ""
            return f"{library}-{Version(self.version).major}.Q{self.options.quantum_depth}{suffix}"

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html

        core_requires = []
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            core_requires.append("xz_utils::xz_utils")
        if self.options.with_lcms:
            core_requires.append("lcms::lcms")
        if self.options.with_openexr:
            core_requires.append("openexr::openexr")
        if self.options.with_heic:
            core_requires.append("libheif::libheif")
        if self.options.with_jbig:
            core_requires.append("jbig::jbig")
        if self.options.with_jpeg:
            core_requires.append("{0}::{0}".format(self.options.with_jpeg))
        if self.options.with_openjp2:
            core_requires.append("openjpeg::openjpeg")
        if self.options.with_pango:
            core_requires.append("pango::pango")
        if self.options.with_png:
            core_requires.append("libpng::libpng")
        if self.options.with_tiff:
            core_requires.append("libtiff::libtiff")
        if self.options.with_webp:
            core_requires.append("libwebp::libwebp")
        if self.options.with_xml2:
            core_requires.append("libxml2::libxml2")
        if self.options.with_freetype:
            core_requires.append("freetype::freetype")

        if is_msvc(self):
            if not self.options.shared:
                self.cpp_info.components["MagickCore"].libs.append(self._libname("coders"))
        if self.settings.os == "Linux":
            self.cpp_info.components["MagickCore"].system_libs.append("pthread")

        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_QUANTUM_DEPTH={self.options.quantum_depth}")
        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_HDRI_ENABLE={int(bool(self.options.hdri))}")
        self.cpp_info.components["MagickCore"].defines.append(
            "_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1"
        )

        include_dir_root = os.path.join("include", f"ImageMagick-{Version(self.version).major}")
        self.cpp_info.components["MagickCore"].includedirs = [include_dir_root]
        self.cpp_info.components["MagickCore"].libs.append(self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].set_property("pkg_config_name", "MagicCore")

        self.cpp_info.components[self._libname("MagickCore")].requires = ["MagickCore"]
        self.cpp_info.components[self._libname("MagickCore")].set_property(
            "pkg_config_name", self._libname("MagickCore")
        )

        self.cpp_info.components["MagickWand"].includedirs = [os.path.join(include_dir_root, "MagickWand")]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].set_property("pkg_config_name", "MagickWand")

        self.cpp_info.components[self._libname("MagickWand")].requires = ["MagickWand"]
        self.cpp_info.components[self._libname("MagickWand")].set_property("pkg_config_name", "MagickWand")

        self.cpp_info.components["Magick++"].includedirs = [os.path.join(include_dir_root, "Magick++")]
        self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
        self.cpp_info.components["Magick++"].requires = ["MagickWand"]
        self.cpp_info.components["Magick++"].set_property("pkg_config_name", ["Magick++", self._libname("Magick++")])

        self.cpp_info.components[self._libname("Magick++")].requires = ["Magick++"]
        self.cpp_info.components[self._libname("Magick++")].set_property("pkg_config_name", self._libname("Magick++"))

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
