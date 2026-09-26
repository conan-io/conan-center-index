from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, copy, rmdir, rm, save, load, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.env import VirtualRunEnv, Environment
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import glob
import os
import shutil
import stat


class ImageMagickConan(ConanFile):
    name = "imagemagick"
    license = "ImageMagick"
    homepage = "https://imagemagick.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, "
        "converting, and editing raster image and vector image files."
    )
    topics = ("imagemagick", "image", "graphics", "convert", "magick")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared":            [True, False],
        "fPIC":              [True, False],
        # --- ImageMagick-specific core options ---
        "hdri":              [True, False],
        "quantum_depth":     [8, 16, 32],
        "with_openmp":       [True, False],
        "utilities":         [True, False],
        # --- Delegate libraries (CCI available) ---
        "with_zlib":         [True, False],
        "with_bzlib":        [True, False],
        "with_lzma":         [True, False],
        "with_zstd":         [True, False],
        "with_png":          [True, False],
        "with_jpeg":         [None, "libjpeg", "libjpeg-turbo"],
        "with_tiff":         [True, False],
        "with_webp":         [True, False],
        "with_freetype":     [True, False],
        "with_xml2":         [True, False],
        "with_fontconfig":   [True, False],
        "with_lcms":         [True, False],
        "with_openexr":      [True, False],
        "with_heic":         [True, False],
        "with_jbig":         [True, False],
        "with_openjp2":      [True, False],
        "with_jxl":          [True, False],
        "with_raw":          [True, False],
        "with_fftw":         [True, False],
        "with_pango":        [True, False],
        "with_zip":          [True, False],
        "with_djvu":         [True, False],
        "with_lqr":          [True, False],
        "with_uhdr":         [True, False],
        # --- Delegate libraries (NOT in CCI — commented out in consumer) ---
        # "with_raqm":       [True, False],  # no CCI recipe (libraqm)
        # "with_rsvg":       [True, False],  # no CCI recipe (librsvg)
        # "with_wmf":        [True, False],  # no CCI recipe (libwmf)
        # "with_autotrace":  [True, False],  # no CCI recipe
        # "with_flif":       [True, False],  # no CCI recipe
        # "with_fpx":        [True, False],  # no CCI recipe (FlashPIX)
        # "with_gvc":        [True, False],  # no CCI recipe (graphviz)
    }
    default_options = {
        "shared":            False,
        "fPIC":              True,
        "hdri":              True,
        "quantum_depth":     16,
        "with_openmp":       True,
        "utilities":         False,
        "with_zlib":         True,
        "with_bzlib":        True,
        "with_lzma":         True,
        "with_zstd":         True,
        "with_png":          True,
        "with_jpeg":         "libjpeg",
        "with_tiff":         True,
        "with_webp":         True,
        "with_freetype":     True,
        "with_xml2":         True,
        "with_fontconfig":   False,
        "with_lcms":         True,
        "with_openexr":      False,
        "with_heic":         False,
        "with_jbig":         False,
        "with_openjp2":      False,
        "with_jxl":          False,
        "with_raw":          False,
        "libraw/*:build_thread_safe": True,
        "with_fftw":         False,
        "with_pango":        False,
        "with_zip":          False,
        "with_djvu":         False,
        "with_lqr":          False,
        "with_uhdr":         False,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cl_wrapper.sh", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "lib_wrapper.sh", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # OpenMP: AC_OPENMP detection can fail on Windows MSYS2 builds
            self.options.with_openmp = False
            # fontconfig is a FreeDesktop/Linux font discovery system;
            # Windows uses GDI font APIs instead
            self.options.with_fontconfig = False
        if self.settings.compiler == "apple-clang":
            # apple-clang does not ship libomp by default
            self.options.with_openmp = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.3]")
        if self.options.with_bzlib:
            self.requires("bzip2/[>=1.0]")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6]")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0]")
        if self.options.with_tiff:
            self.requires("libtiff/[>=4.6]")
        if self.options.with_webp:
            self.requires("libwebp/[>=1.3]")
        if self.options.with_freetype:
            self.requires("freetype/[>=2.13]")
        if self.options.with_xml2:
            self.requires("libxml2/[>=2.12]")
        if self.options.with_fontconfig:
            self.requires("fontconfig/[>=2.15]")
        if self.options.with_lcms:
            self.requires("lcms/[>=2.16]")
        if self.options.with_openexr:
            self.requires("openexr/[>=3.2]")
        if self.options.with_heic:
            self.requires("libheif/[>=1.17]")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_openjp2:
            self.requires("openjpeg/[>=2.5]")
        if self.options.with_jxl:
            self.requires("libjxl/[>=0.9]")
        if self.options.with_raw:
            self.requires("libraw/[>=0.21]")
        if self.options.with_fftw:
            self.requires("fftw/[>=3.3]")
        if self.options.with_pango:
            self.requires("pango/[>=1.50]")
        if self.options.with_zip:
            self.requires("libzip/[>=1.10]")
        if self.options.with_djvu:
            self.requires("djvulibre/[>=3.5]")
        if self.options.with_lqr:
            self.requires("liblqr/[>=0.4]")
        if self.options.with_uhdr:
            self.requires("libultrahdr/[>=1.3]")

    def build_requirements(self):
        self.tool_requires("pkgconf/[>=2.1]")
        if self._is_windows_cl:
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            # NOTE: We intentionally do NOT tool_requires autoconf/automake/libtool on Windows.
            # Conan CCI's autoconf/2.71 has an AC_OPENMP m4_syscmd bug on Windows, and libtool/2.4.7 transitively requires it (creating a version conflict with 2.72).
            # We install all autotools from MSYS2 pacman in build() instead — MSYS2 rolling-release has autoconf 2.73 which doesn't have this bug.
        else:
            self.tool_requires("libtool/2.4.7")

    @property
    def _is_msvc(self):
        return is_msvc(self)

    @property
    def _is_windows_cl(self):
        """True for any MSVC-compatible compiler on Windows (cl.exe or clang-cl).
        Both use the same headers, runtime, MSYS2 autotools path, and need
        identical workarounds (ssize_t, -TP, -EHsc, .pc Cflags fix, etc.)."""
        return is_msvc(self) or (
            self.settings.os == "Windows"
            and str(self.settings.compiler) == "clang"
        )

    @property
    def _abi_suffix(self):
        """ABI suffix used by ImageMagick in library/include naming, e.g. Q16HDRI."""
        s = f"Q{self.options.quantum_depth}"
        if self.options.hdri:
            s += "HDRI"
        return s

    @property
    def _major_version(self):
        return str(self.version).split(".")[0]

    def _create_cl_wrappers(self):
        """Create MSYS2 bash wrappers so libtool sees cc_basename=cl → MSVC mode.

        Naming the wrapper ``cl`` makes libtool's ``case $cc_basename``
        patterns (``cl*|icl*``) match → enters native MSVC codepath for
        DLL/import-lib creation, static archive (``lib -OUT:``), etc.

        The wrapper also translates GCC-style ``-lfoo`` → ``foo.lib`` and
        ``-Lpath`` → ``-libpath:path`` (passed to the linker via ``-link``).
        Neither cl.exe nor clang-cl understand these GCC flags natively,
        which is fine for static builds (symbols resolved at consumer link
        time) but fatal for shared builds (DLLs must resolve all symbols).

        For MSVC: wraps cl.exe / lib.exe (found from PATH at runtime —
        conanbuild.sh ensures VCVars tools are in PATH).
        For clang-cl: wraps clang-cl / llvm-lib (resolved at generate time).

        The wrapper scripts (cl_wrapper.sh, lib_wrapper.sh) are external
        files read from the recipe directory.  They use ``$REAL_CC`` /
        ``$REAL_LIB`` env vars (set via conanbuild.sh) to locate the real
        compiler/archiver, so no f-string injection is needed.

        Returns the wrapper directory path (Windows-style).
        """
        wrapper_dir = os.path.join(self.build_folder, "_cl_wrappers")
        os.makedirs(wrapper_dir, exist_ok=True)

        if self._is_msvc:
            # MSVC: wrapper calls cl.exe / lib.exe from PATH at runtime.
            # In MSYS2, "cl.exe" (with .exe extension) unambiguously refers to the Windows PE executable, not this "cl" bash script.
            # conanbuild.sh adds the MSVC tools directory to PATH.
            real_cc = "cl.exe"
            real_lib = "lib.exe"
        else:
            # clang-cl: resolve full path from Conan profile, PATH, or vswhere.
            compilers = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
            clang_cl = compilers.get("c") or compilers.get("cpp") or "clang-cl"
            clang_cl = shutil.which(clang_cl)
            if not clang_cl:
                # vcvarsall not sourced — locate via vswhere
                vswhere = os.path.join(os.environ.get("ProgramFiles(x86)", ""),
                                       "Microsoft Visual Studio", "Installer", "vswhere.exe")
                if os.path.isfile(vswhere):
                    import subprocess
                    vs_path = subprocess.check_output(
                        [vswhere, "-latest", "-property", "installationPath"],
                        text=True).strip()
                    candidate = os.path.join(vs_path, "VC", "Tools", "Llvm", "x64", "bin", "clang-cl.exe")
                    if os.path.isfile(candidate):
                        clang_cl = candidate
            if not clang_cl or not os.path.isfile(clang_cl):
                raise ConanInvalidConfiguration(
                    f"clang-cl not found (tried profile conf, PATH, vswhere). Got: {clang_cl}")
            tool_dir = os.path.dirname(clang_cl)

            def _to_msys(p):
                """Convert a Windows path to MSYS2 /drive/... format."""
                p = p.replace("\\", "/")
                if len(p) >= 2 and p[1] == ":":
                    p = f"/{p[0].lower()}{p[2:]}"
                return p

            real_cc = _to_msys(clang_cl)
            real_lib = _to_msys(os.path.join(tool_dir, "llvm-lib.exe"))

        # --- Install wrapper scripts from export sources ----------
        # The scripts use $REAL_CC / $REAL_LIB env vars to call the real compiler/archiver.
        # export_sources() copies them to the export base; with basic_layout(src_folder="src"),
        # self.source_folder = <base>/src, so the scripts are one level up.
        export_base = os.path.dirname(self.source_folder)
        for src_name, dst_name in [("cl_wrapper.sh", "cl"), ("lib_wrapper.sh", "lib")]:
            src_path = os.path.join(export_base, src_name)
            dst_path = os.path.join(wrapper_dir, dst_name)
            content = load(self, src_path)
            save(self, dst_path, content)
            os.chmod(dst_path, os.stat(dst_path).st_mode | stat.S_IEXEC)

        # --- Inject REAL_CC / REAL_LIB into conanbuild environment -
        env = Environment()
        env.define("REAL_CC", real_cc)
        env.define("REAL_LIB", real_lib)
        envvars = env.vars(self, scope="build")
        envvars.save_script("conanbuild_cl_wrappers")

        return wrapper_dir

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # VirtualRunEnv with scope="build" merges LD_LIBRARY_PATH into conanbuild.sh (sourced by Autotools) so that configure can
        # execute test programs linked against shared deps (libheif, libx265 on Linux).
        # Default scope="host" only writes conanrun.sh which Autotools ignores.
        run_env = VirtualRunEnv(self)
        run_env.generate(scope="build")
        if self.settings.os != "Windows":
            deps = AutotoolsDeps(self)
            deps.generate()
        pkgconfig = PkgConfigDeps(self)
        # ImageMagick's configure.ac does PKG_CHECK_MODULES(UHDR, libuhdr >= 1.3.0) but Conan generates "libultrahdr.pc" (Conan package name).
        # Fix the name.
        pkgconfig.set_property("libultrahdr", "pkg_config_name", "libuhdr")
        # ImageMagick's configure.ac does PKG_CHECK_MODULES(RAW, libraw_r >= 0.14.8)
        # — it requires the thread-safe variant. Conan generates "libraw.pc".
        pkgconfig.set_property("libraw", "pkg_config_name", "libraw_r")
        pkgconfig.generate()
        if self._is_windows_cl:
            # Fix PkgConfigDeps component-level .pc files missing Cflags.
            # Conan's PkgConfigDeps sometimes omits `Cflags: -I"${includedir}"` in component .pc files (e.g., libzstd.pc).
            # Without Cflags, configure's PKG_CHECK_MODULES can detect the package but the include path never reaches the Makefile CPPFLAGS,
            # causing "Cannot open include file" during make.
            gen_dir = os.path.join(self.build_folder, "conan")
            for pc_file in glob.glob(os.path.join(gen_dir, "*.pc")):
                content = load(self, pc_file)
                if "includedir=" in content and "Cflags:" not in content:
                    save(self, pc_file, content.rstrip() + '\nCflags: -I"${includedir}"\n')

        tc = AutotoolsToolchain(self)
        yes_no = lambda opt: "yes" if opt else "no"

        tc.configure_args.extend([
            f"--enable-shared={'yes' if self.options.shared else 'no'}",
            f"--enable-static={'no' if self.options.shared else 'yes'}",
            f"--enable-hdri={'yes' if self.options.hdri else 'no'}",
            f"--with-quantum-depth={self.options.quantum_depth}",
            f"--enable-openmp={'yes' if self.options.with_openmp else 'no'}",
            f"--with-utilities={'yes' if self.options.utilities else 'no'}",
            # Delegate libraries
            f"--with-zlib={yes_no(self.options.with_zlib)}",
            f"--with-bzlib={yes_no(self.options.with_bzlib)}",
            f"--with-lzma={yes_no(self.options.with_lzma)}",
            f"--with-zstd={yes_no(self.options.with_zstd)}",
            f"--with-png={yes_no(self.options.with_png)}",
            f"--with-jpeg={yes_no(self.options.with_jpeg)}",
            f"--with-tiff={yes_no(self.options.with_tiff)}",
            f"--with-webp={yes_no(self.options.with_webp)}",
            f"--with-freetype={yes_no(self.options.with_freetype)}",
            f"--with-xml={yes_no(self.options.with_xml2)}",
            f"--with-fontconfig={yes_no(self.options.with_fontconfig)}",
            f"--with-lcms={yes_no(self.options.with_lcms)}",
            f"--with-openexr={yes_no(self.options.with_openexr)}",
            f"--with-heic={yes_no(self.options.with_heic)}",
            f"--with-jbig={yes_no(self.options.with_jbig)}",
            f"--with-openjp2={yes_no(self.options.with_openjp2)}",
            f"--with-jxl={yes_no(self.options.with_jxl)}",
            f"--with-raw={yes_no(self.options.with_raw)}",
            f"--with-fftw={yes_no(self.options.with_fftw)}",
            f"--with-pango={yes_no(self.options.with_pango)}",
            f"--with-zip={yes_no(self.options.with_zip)}",
            f"--with-djvu={yes_no(self.options.with_djvu)}",
            f"--with-lqr={yes_no(self.options.with_lqr)}",
            f"--with-uhdr={yes_no(self.options.with_uhdr)}",
            # Always disable: not available or not needed
            "--without-x",
            "--without-perl",
            "--with-magick-plus-plus=yes",
            "--with-modules=no",
            "--disable-docs",
            "--disable-installed",
            # Delegates with no CCI recipe — always off
            "--without-raqm",
            "--without-rsvg",
            "--without-wmf",
            "--without-autotrace",
            "--without-flif",
            "--without-fpx",
            "--without-gvc",
            "--without-dps",
            "--without-gslib",
            "--without-dmr",
        ])

        if self.settings.os == "Windows":
            # ImageMagick's configure.ac has native_win32_build checks for mingw;
            # when building with MSVC via MSYS2, we may need to hint some detections
            tc.extra_cflags.append("-DWIN32")
            tc.extra_cxxflags.append("-DWIN32")
            if self.settings.arch == "x86_64":
                tc.extra_cflags.append("-DWIN64")
                tc.extra_cxxflags.append("-DWIN64")
            if self._is_windows_cl:
                # Enable C++ exception handling. MSVC cl.exe enables this by default, but clang-cl does not.
                # It requires explicit -EHsc.
                # Without it, configure's C++ exception syntax test fails and Magick++ (Blob.cpp etc.) can't use try/catch.
                tc.extra_cxxflags.append("-EHsc")
                # MSVC lacks POSIX ssize_t — inject via command line.
                tc.extra_cflags.append("-Dssize_t=ptrdiff_t")
                tc.extra_cxxflags.append("-Dssize_t=ptrdiff_t")
                # Force libtool to skip file_magic format checks — MSVC .lib files are MS-COFF, not ELF/PE,
                # making the default file_magic test fail with "none of the candidates passed a file format test".
                # pass_all accepts every library unconditionally.
                tc.configure_args.append("lt_cv_deplibs_check_method=pass_all")
                # --- cl wrapper approach ------------------------------------------------------------------------------------------
                # Create "cl" / "lib" MSYS2 bash wrappers so libtool sees cc_basename=cl → enters native MSVC codepath for DLL /
                # import-lib creation, static archives, etc.
                # The wrappers also translate GCC-style -l/-L flags to MSVC-style (foo.lib / -libpath:path), fixing AC_CHECK_LIB and
                # pkg-config link tests in one shot.
                # For MSVC: wraps cl.exe / lib.exe (from VCVars PATH).
                # For clang-cl: wraps clang-cl / llvm-lib.
                wrapper_dir = self._create_cl_wrappers()
                msys_dir = wrapper_dir.replace("\\", "/")
                tc.configure_args.extend([
                    f"CC={msys_dir}/cl",
                    f"CXX={msys_dir}/cl",
                ])
            if not self._is_msvc:
                # Suppress all warnings from upstream ImageMagick code.
                tc.extra_cflags.append("-w")
                tc.extra_cxxflags.append("-w")
            # Windows system libraries needed for Registry, GDI+, COM, etc.
            # The cl wrapper translates -lfoo → foo.lib for the linker.
            tc.extra_ldflags.append("-ladvapi32")
            # GDI+ for EMF/WMF coders
            tc.extra_ldflags.append("-lgdi32")
            tc.extra_ldflags.append("-luser32")
            tc.extra_ldflags.append("-lole32")
            tc.extra_ldflags.append("-loleaut32")
            if self._is_windows_cl:
                # Add all Conan dependency library directories to LDFLAGS.
                # When building shared libraries (DLLs), libtool invokes the linker with -lfoo from AC_CHECK_LIB / PKG_CHECK_MODULES
                # but may not propagate the corresponding -Lpath from .pc files.
                # Libraries found via AC_CHECK_LIB (e.g. bz2, jpeg) have no pkg-config entry in configure.ac, so their -L path is
                # never added to the link command.
                # The cl wrapper translates -Lpath → -libpath:path (after -link) for the MSVC linker.
                for dep in self.dependencies.host.values():
                    for libdir in dep.cpp_info.libdirs:
                        abs_dir = libdir if os.path.isabs(libdir) else os.path.join(dep.package_folder, libdir)
                        if os.path.isdir(abs_dir):
                            tc.extra_ldflags.append(f"-L{abs_dir.replace(os.sep, '/')}")
                # AC_CHECK_LIB for bz2/jpeg: the cl wrapper translates -lbz2 -> bz2.lib and -ljpeg -> jpeg.lib, but actual Conan
                # library filenames may differ (e.g. libjpeg.lib).
                # Pre-seed the configure cache so the redundant check doesn't fail.
                if self.options.with_bzlib:
                    tc.configure_args.append("ac_cv_lib_bz2_BZ2_bzDecompress=yes")
                if self.options.with_jpeg:
                    tc.configure_args.append("ac_cv_lib_jpeg_jpeg_read_header=yes")

        # Workaround: Conan's conanbuildenv (from tool_requires: pkgconf, libtool, etc.) resets PKG_CONFIG_PATH="" because
        # no tool_requires defines it, stomping the value set by conanautotoolstoolchain.sh. Since PKG_CONFIG_PATH is an
        # autoconf "precious variable" (AC_ARG_VAR in pkg.m4), passing it on the configure command line takes precedence
        # over the (empty) environment value.
        # Force using forward slashes: on Windows/MSYS2, os.path.join produces backslash paths which bash interprets as escapes.
        tc.configure_args.append(f"PKG_CONFIG_PATH={os.path.join(self.build_folder, 'conan').replace(os.sep, '/')}")

        tc.generate()

    def build(self):
        # Apply patches to source files (configure.ac, headers) BEFORE running autoreconf, so generated files reflect the fixes.
        # Patches:
        #   0001: Fix ZSTD PKG_CHECK_MODULES prefix (LIBZSTD → ZSTD)
        #   0002: Fix magick_fallthrough for MSVC C mode (__cplusplus guard)
        apply_conandata_patches(self)

        # Install autotools from MSYS2 pacman instead of Conan tool_requires.
        # Conan CCI's autoconf/2.71 has an AC_OPENMP m4_syscmd bug (cwd check) on Windows, autoconf/2.72 conflicts with libtool's
        # transitive dep on 2.71.
        # MSYS2 rolling-release has autoconf >= 2.72 which works.
        if self._is_windows_cl:
            self.run("pacman -Sy --noconfirm --needed "
                     "autoconf-wrapper autoconf2.72 "
                     "automake-wrapper automake1.16 "
                     "libtool")

        autotools = Autotools(self)
        # Regenerate configure + Makefile.in from patched .ac/.am sources
        autotools.autoreconf()
        autotools.configure()

        if self._is_windows_cl:
            # Post-configure Makefile injection: add flags that CANNOT be in AutotoolsToolchain because they break configure checks.
            makefile = os.path.join(self.build_folder, "Makefile")
            content = load(self, makefile)

            # 1. Compile coders/emf.c as C++.
            #    It includes <gdiplus.h> which uses C++ features (namespaces, new/delete).
            #    Mirrors CCI VisualMagick CompileAs=CompileAsCpp for this file.
            #    Cannot use global -TP in CFLAGS: it would force all .c files to C++ mode, breaking dng.c -> libraw -> <fstream> -> MSVC STL
            #    (clang-cl C++23 can't parse __msvc_ostream.hpp out of context).
            #    Instead, add a per-target CFLAGS override via GNU make syntax.
            content += ("\n# Per-file C++ mode for emf.c (needs <gdiplus.h>)\n"
                        "coders/MagickCore_libMagickCore_7_Q16HDRI_la-emf.lo: "
                        "CFLAGS += -TP\n"
                        "coders/emf_la-emf.lo: CFLAGS += -TP\n")

            # 2. Inject _DLL/_LIB and _MT defines removed from configure.ac by patch 0003.
            #    ImageMagick's configure.ac used to put these in CPPFLAGS, but -D_DLL makes CRT headers declare stdio functions
            #    as dllimport which is incompatible with -MT (static CRT) and causes LNK2019 for fopen/ferror during AC_CHECK_SIZEOF.
            #    We only need them at build time, so inject after configure.
            dll_define = "-D_DLL" if self.options.shared else "-D_LIB"
            content = content.replace(
                "\nCPPFLAGS = ", f"\nCPPFLAGS = {dll_define} -D_MT ", 1)

            save(self, makefile, content)

        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Keep etc/ImageMagick-7/ (runtime config XMLs: colors.xml, policy.xml, coder.xml, ...)
        # and share/ImageMagick-7/ (locale XMLs: english.xml, francais.xml, locale.xml).
        # IM needs these at runtime unless built with zero-configuration (built-in XML blobs).
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        major = self._major_version
        abi = self._abi_suffix
        includedir = os.path.join("include", f"ImageMagick-{major}")

        # --- Magick++ (C++ API) — the main consumer target ------------------------------------------------------------------------
        self.cpp_info.set_property("cmake_file_name", "ImageMagick")
        self.cpp_info.set_property("cmake_target_name", "ImageMagick::Magick++")
        self.cpp_info.set_property("pkg_config_name", f"Magick++-{major}.{abi}")

        # Only expose the top-level ImageMagick-7/ include directory.
        # All internal headers use prefixed includes (e.g. #include <MagickCore/xyz.h>) so subdirectory entries are unnecessary.
        # Worse, MagickCore/ contains a semaphore.h that collides with POSIX <semaphore.h> when added as -isystem.
        self.cpp_info.includedirs = [includedir]

        # Library names follow the pattern: LibName-Major.QxxHDRI
        lib_suffix = f"-{major}.{abi}"
        self.cpp_info.libs = [
            f"Magick++{lib_suffix}",
            f"MagickWand{lib_suffix}",
            f"MagickCore{lib_suffix}",
        ]

        self.cpp_info.defines.append(f"MAGICKCORE_QUANTUM_DEPTH={self.options.quantum_depth}")
        self.cpp_info.defines.append(f"MAGICKCORE_HDRI_ENABLE={int(bool(self.options.hdri))}")
        if self.options.shared:
            self.cpp_info.defines.append("_MAGICKDLL_=1")
        else:
            self.cpp_info.defines.append("_MAGICKLIB_=1")

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Macos":
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            # ssize_t is POSIX, not available in MSVC/clang-cl headers.
            # ImageMagick headers use it extensively (image.h, etc.).
            # The build uses -Dssize_t=ptrdiff_t; consumers need it too.
            self.cpp_info.defines.append("ssize_t=ptrdiff_t")
            self.cpp_info.system_libs.extend([
                "gdi32", "user32", "advapi32", "ole32", "oleaut32",
            ])

        # OpenMP runtime: upstream .pc has -fopenmp in Cflags and -lgomp/-lomp in Libs.private,
        # but Conan consumers don't read .pc files — we must expose the runtime lib explicitly.
        # Only needed on Linux/FreeBSD where the runtime is a standalone system library.
        # Windows: /openmp flag auto-links vcomp.lib (MSVC) or libomp.lib (clang-cl).
        # macOS: with_openmp is already forced to False (apple-clang has no libomp).
        if self.options.with_openmp and self.settings.os in ("Linux", "FreeBSD"):
            if self.settings.compiler == "gcc":
                self.cpp_info.system_libs.append("gomp")
            else:
                self.cpp_info.system_libs.append("omp")

        # Expose the config XML directory so consumers can find it at runtime.
        # IM searches MAGICK_CONFIGURE_PATH first, then beside the exe, then hardcoded paths.
        etc_path = os.path.join(self.package_folder, "etc", f"ImageMagick-{self._major_version}")
        if os.path.isdir(etc_path):
            self.runenv_info.define("MAGICK_CONFIGURE_PATH", etc_path)
