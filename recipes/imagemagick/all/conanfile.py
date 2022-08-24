from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conan.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, converting, and editing "
        "raster image and vector image files"
    )
    topics = ("imagemagick", "images", "manipulating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    license = "ImageMagick"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"
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
        "with_openexr": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_openjp2": True,
        "with_pango": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_djvu": False,
        "utilities": True,
    }
    exports_sources = "patches/*"

    _autotools = None

    @property
    def _source_subfolder(self):
        return (
            "ImageMagick"  # name is important, VisualMagick uses relative paths to it
        )

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _modules(self):
        return ["Magick++", "MagickWand", "MagickCore"]

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds of ImageMagick require MFC which cannot currently be sourced from CCI."
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_lcms:
            self.requires("lcms/2.11")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_heic:
            self.requires("libheif/1.12.0")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.0")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.4.0")
        if self.options.with_pango:
            self.requires("pango/1.50.7")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.0")
        if self.options.with_xml2:
            self.requires("libxml2/2.9.10")
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")
        if self.options.with_djvu:
            # FIXME: missing djvu recipe
            self.output.warn(
                "There is no djvu package available on Conan (yet). This recipe will use the one present on the system (if available)."
            )

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version]["source"],
            destination=self._source_subfolder,
            strip_root=True
        )

        if self._is_msvc:
            visualmagick_version = list(
                self.conan_data["sources"][self.version]["visualmagick"].keys()
            )[0]
            tools.files.get(self, 
                **self.conan_data["sources"][self.version]["visualmagick"][
                    visualmagick_version
                ],
                destination="VisualMagick",
                strip_root=True
            )

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            with tools.files.chdir(self, self._source_subfolder):
                env_build = self._build_configure()
                env_build.make()

    def _build_msvc(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.files.patch(self, **patch)

        # FIXME: package LiquidRescale  aka liblqr
        tools.files.replace_in_file(self, 
            os.path.join("VisualMagick", "lqr", "Config.txt"),
            "#define MAGICKCORE_LQR_DELEGATE",
            "",
        )
        # FIXME: package LibRaw
        tools.files.replace_in_file(self, 
            os.path.join("VisualMagick", "libraw", "Config.txt"),
            "#define MAGICKCORE_RAW_R_DELEGATE",
            "",
        )

        # FIXME: package FLIF (FLIF: Free Lossless Image Format)
        tools.files.replace_in_file(self, 
            os.path.join("VisualMagick", "flif", "Config.txt"),
            "#define MAGICKCORE_FLIF_DELEGATE",
            "",
        )

        # FIXME: package librsvg
        tools.files.replace_in_file(self, 
            os.path.join("VisualMagick", "librsvg", "Config.txt"),
            "#define MAGICKCORE_RSVG_DELEGATE",
            "",
        )

        if not self.options.shared:
            for module in self._modules:
                tools.files.replace_in_file(self, 
                    os.path.join("VisualMagick", module, "Config.txt"),
                    "[DLL]",
                    "[STATIC]",
                )
            tools.files.replace_in_file(self, 
                os.path.join("VisualMagick", "coders", "Config.txt"),
                "[DLLMODULE]",
                "[STATIC]\n[DEFINES]\n_MAGICKLIB_",
            )

        if self.settings.arch == "x86_64":
            project = os.path.join("VisualMagick", "configure", "configure.vcxproj")
            tools.files.replace_in_file(self, project, "Win32", "x64")
            tools.files.replace_in_file(self, project, "/MACHINE:I386", "/MACHINE:x64")

        with tools.files.chdir(self, os.path.join("VisualMagick", "configure")):

            toolset = tools.msvs_toolset(self)
            tools.files.replace_in_file(self, 
                "configure.vcxproj",
                "<PlatformToolset>v120</PlatformToolset>",
                "<PlatformToolset>%s</PlatformToolset>" % toolset,
            )

            msbuild = MSBuild(self)
            # fatal error C1189: #error:  Please use the /MD switch for _AFXDLL builds
            msbuild.build_env.flags = ["/MD"]
            msbuild.build(
                project_file="configure.vcxproj",
                platforms={"x86": "Win32"},
                force_vcvars=True,
            )

            # https://github.com/ImageMagick/ImageMagick-Windows/blob/master/AppVeyor/Build.ps1
            command = ["configure.exe", "/noWizard"]
            msvc_version = {
                9: "/VS2002",
                10: "/VS2010",
                11: "/VS2012",
                12: "/VS2013",
                14: "/VS2015",
                15: "/VS2017",
                16: "/VS2019",
                17: "/VS2022",
            }.get(int(str(self.settings.compiler.version)))
            runtime = {"MT": "/smt", "MTd": "/smtd", "MD": "/dmt", "MDd": "/mdt"}.get(
                str(self.settings.compiler.runtime)
            )
            command.append(runtime)
            command.append(msvc_version)
            command.append("/hdri" if self.options.hdri else "/noHdri")
            command.append("/Q%s" % self.options.quantum_depth)
            if self.settings.arch == "x86_64":
                command.append("/x64")
            command = " ".join(command)

            self.output.info(command)
            self.run(command, run_environment=True)

        # disable incorrectly detected OpenCL
        baseconfig = os.path.join(
            self._source_subfolder, "MagickCore", "magick-baseconfig.h"
        )
        tools.files.replace_in_file(self, 
            baseconfig,
            "#define MAGICKCORE__OPENCL",
            "#undef MAGICKCORE__OPENCL",
            strict=False,
        )
        tools.files.replace_in_file(self, 
            baseconfig,
            "#define MAGICKCORE_HAVE_CL_CL_H",
            "#undef MAGICKCORE_HAVE_CL_CL_H",
            strict=False,
        )

        suffix = {
            "MT": "StaticMT",
            "MTd": "StaticMTD",
            "MD": "DynamicMT",
            "MDd": "DynamicMT",
        }.get(str(self.settings.compiler.runtime))

        # GdiPlus requires C++, but ImageMagick has *.c files
        project = (
            "IM_MOD_emf_%s.vcxproj" % suffix
            if self.options.shared
            else "CORE_coders_%s.vcxproj" % suffix
        )
        tools.files.replace_in_file(self, 
            os.path.join("VisualMagick", "coders", project),
            '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">',
            '<ClCompile Include="..\\..\\ImageMagick\\coders\\emf.c">\n'
            "<CompileAs>CompileAsCpp</CompileAs>",
        )

        for module in self._modules:
            with tools.files.chdir(self, os.path.join("VisualMagick", module)):
                msbuild = MSBuild(self)
                msbuild.build(
                    project_file="CORE_%s_%s.vcxproj" % (module, suffix),
                    upgrade_project=False,
                    platforms={"x86": "Win32", "x86_64": "x64"},
                )

        with tools.files.chdir(self, os.path.join("VisualMagick", "coders")):
            pattern = (
                "IM_MOD_*_%s.vcxproj" % suffix
                if self.options.shared
                else "CORE_coders_%s.vcxproj" % suffix
            )
            projects = glob.glob(pattern)
            for project in projects:
                msbuild = MSBuild(self)
                msbuild.build(
                    project_file=project,
                    upgrade_project=False,
                    platforms={"x86": "Win32", "x86_64": "x64"},
                )

    def _build_configure(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows
        )

        # FIXME: workaround for xorg/system adding system includes https://github.com/conan-io/conan-center-index/issues/6880
        if "/usr/include/uuid" in self._autotools.include_paths:
            self._autotools.include_paths.remove("/usr/include/uuid")


        def yes_no(o):
            return "yes" if o else "no"

        args = [
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
        self._autotools.configure(args=args)

        return self._autotools

    def package(self):
        with tools.files.chdir(self, self._source_subfolder):
            env_build = self._build_configure()
            env_build.install()

        with tools.files.chdir(self, self.package_folder):
            # remove undesired files
            tools.files.rmdir(self, os.path.join("lib", "pkgconfig"))  # pc files
            tools.files.rmdir(self, "etc")
            tools.files.rmdir(self, "share")
            tools.files.rm(self, "lib", "*.la")

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(
                pattern="*CORE_*.lib",
                dst="lib",
                src=os.path.join("VisualMagick", "lib"),
                keep_path=False,
            )

            self.copy(
                pattern="*CORE_*.dll",
                dst="bin",
                src=os.path.join("VisualMagick", "bin"),
                keep_path=False,
            )
            self.copy(
                pattern="*IM_MOD_*.dll",
                dst="bin",
                src=os.path.join("VisualMagick", "bin"),
                keep_path=False,
            )
            for module in self._modules:
                self.copy(
                    pattern="*.h",
                    dst=os.path.join(
                        "include",
                        "ImageMagick-%s" % tools.Version(self.version).major,
                        module,
                    ),
                    src=os.path.join(self._source_subfolder, module),
                )

    def _libname(self, library):
        if self._is_msvc:
            infix = "DB" if self.settings.build_type == "Debug" else "RL"
            return "CORE_%s_%s_" % (infix, library)
        else:
            suffix = "HDRI" if self.options.hdri else ""
            return "%s-%s.Q%s%s" % (
                library,
                tools.Version(self.version).major,
                self.options.quantum_depth,
                suffix,
            )

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

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

        if self._is_msvc:
            if not self.options.shared:
                self.cpp_info.components["MagickCore"].libs.append(
                    self._libname("coders")
                )
        if self.settings.os == "Linux":
            self.cpp_info.components["MagickCore"].system_libs.append("pthread")

        self.cpp_info.components["MagickCore"].defines.append(
            "MAGICKCORE_QUANTUM_DEPTH=%s" % self.options.quantum_depth
        )
        self.cpp_info.components["MagickCore"].defines.append(
            "MAGICKCORE_HDRI_ENABLE=%s" % int(bool(self.options.hdri))
        )
        self.cpp_info.components["MagickCore"].defines.append(
            "_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1"
        )

        imagemagick_include_dir = (
            "include/ImageMagick-%s" % tools.Version(self.version).major
        )

        self.cpp_info.components["MagickCore"].includedirs = [imagemagick_include_dir]
        self.cpp_info.components["MagickCore"].libs.append(self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].names["pkg_config"] = ["MagicCore"]

        self.cpp_info.components[self._libname("MagickCore")].requires = ["MagickCore"]
        self.cpp_info.components[self._libname("MagickCore")].names["pkg_config"] = [
            self._libname("MagickCore")
        ]

        self.cpp_info.components["MagickWand"].includedirs = [
            imagemagick_include_dir + "/MagickWand"
        ]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].names["pkg_config"] = ["MagickWand"]

        self.cpp_info.components[self._libname("MagickWand")].requires = ["MagickWand"]
        self.cpp_info.components[self._libname("MagickWand")].names[
            "pkg_config"
        ] = self._libname("MagickWand")

        self.cpp_info.components["Magick++"].includedirs = [
            imagemagick_include_dir + "/Magick++"
        ]
        self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
        self.cpp_info.components["Magick++"].requires = ["MagickWand"]
        self.cpp_info.components["Magick++"].names["pkg_config"] = [
            "Magick++",
            self._libname("Magick++"),
        ]

        self.cpp_info.components[self._libname("Magick++")].requires = ["Magick++"]
        self.cpp_info.components[self._libname("Magick++")].names[
            "pkg_config"
        ] = self._libname("Magick++")
