import glob
import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.files import chdir, copy, get, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.intel import IntelCC
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OneTBBConan(ConanFile):
    name = "onetbb"
    description = (
        "oneAPI Threading Building Blocks (oneTBB) lets you easily write parallel "
        "C++ programs that take full advantage of multicore performance, that "
        "are portable, composable and have future-proof scalability."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tbbmalloc": [True, False],
        "tbbproxy": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tbbmalloc": False,
        "tbbproxy": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_clanglc(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    @property
    def _base_compiler(self):
        base = self.settings.get_safe("compiler.base")
        if base:
            return self.settings.compiler.base
        return self.settings.compiler

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbproxy

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if is_apple_os(self):
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "8.0":
                raise ConanInvalidConfiguration(f"{self.name} {self.version} couldn't be built by apple-clang < 8.0")
        if not self.options.shared:
            self.output.warning("oneTBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and (not self.options.shared or not self.options.tbbmalloc):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmaloc and shared options")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.conf_info.get("tools.gnu:make_program", check_type=str):
                self.tool_requires("make/4.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if str(self._base_compiler) in ["Visual Studio", "msvc"]:
            save(
                self,
                os.path.join(self.source_folder, "build", "big_iron_msvc.inc"),
                # copy of big_iron.inc adapted for MSVC
                textwrap.dedent(f"""\
                    LIB_LINK_CMD = {"xilib" if self.settings.compiler == "intel-cc" else "lib"}.exe
                    LIB_OUTPUT_KEY = /OUT:
                    LIB_LINK_FLAGS =
                    LIB_LINK_LIBS =
                    DYLIB_KEY =
                    override CXXFLAGS += -D__TBB_DYNAMIC_LOAD_ENABLED=0 -D__TBB_SOURCE_DIRECTLY_INCLUDED=1
                    ITT_NOTIFY =
                    DLL = lib
                    LIBEXT = lib
                    LIBPREF =
                    LIBDL =
                    TBB.DLL = $(LIBPREF)tbb$(DEBUG_SUFFIX).$(LIBEXT)
                    LINK_TBB.LIB = $(TBB.DLL)
                    TBB.DEF =
                    TBB_NO_VERSION.DLL =
                    MALLOC.DLL = $(LIBPREF)tbbmalloc$(DEBUG_SUFFIX).$(LIBEXT)
                    LINK_MALLOC.LIB = $(MALLOC.DLL)
                    MALLOC.DEF =
                    MALLOC_NO_VERSION.DLL =
                    MALLOCPROXY.DLL =
                    MALLOCPROXY.DEF =
                """),
            )
            if not self.options.shared:
                tc.make_args.append("extra_inc=big_iron_msvc.inc")
        else:
            if not self.options.shared:
                tc.make_args.append("extra_inc=big_iron.inc")

        arch = {
            "x86": "ia32",
            "x86_64": "intel64",
            "armv7": "armv7",
            "armv8": "arm64" if (self.settings.os == "iOS" or is_apple_os(self)) else "aarch64",
        }[str(self.settings.arch)]
        tc.make_args.append(f"arch={arch}")

        if self.settings.os == "iOS":
            tc.make_args.append("target=ios")

        if str(self._base_compiler) in ("gcc", "clang", "apple-clang"):
            if str(self._base_compiler.libcxx) in ("libstdc++", "libstdc++11"):
                tc.make_args.append("stdlib=libstdc++")
            elif str(self._base_compiler.libcxx) == "libc++":
                tc.make_args.append("stdlib=libc++")

            if str(self.settings.compiler) == "intel-cc":
                tc.make_args.append("compiler=icc")
            elif str(self.settings.compiler) in ("clang", "apple-clang"):
                tc.make_args.append("compiler=clang")
            else:
                tc.make_args.append("compiler=gcc")

            if self.settings.os in ["Linux", "FreeBSD"]:
                # runtime is supposed to track the version of the c++ stdlib,
                # the version of glibc, and the version of the linux kernel.
                # However, it isn't actually used anywhere other than for
                # logging and build directory names.
                # TBB computes the value of this variable using gcc, which we
                # don't necessarily want to require when building this recipe.
                # Setting it to a dummy value prevents TBB from calling gcc.
                tc.make_args.append("runtime=gnu")
        elif str(self._base_compiler) in ["Visual Studio", "msvc"]:
            if is_msvc_static_runtime(self):
                runtime = "vc_mt"
            else:
                if is_msvc(self):
                    runtime = {
                        "8": "vc8",
                        "9": "vc9",
                        "10": "vc10",
                        "11": "vc11",
                        "12": "vc12",
                        "14": "vc14",
                        "15": "vc14.1",
                        "16": "vc14.2",
                    }.get(str(self._base_compiler.version), "vc14.2")
                else:
                    runtime = {
                        "190": "vc14",
                        "191": "vc14.1",
                        "192": "vc14.2",
                    }.get(str(self._base_compiler.version), "vc14.2")
            tc.make_args.append(f"runtime={runtime}")

            if self.settings.compiler == "intel-cc":
                tc.make_args.append("compiler=icl")
            else:
                tc.make_args.append("compiler=cl")

        tc.generate()

        if self.settings.compiler == "intel-cc":
            intelcc = IntelCC(self)
            intelcc.generate()
        elif is_msvc(self):
            # intentionally not using vcvars for clang-cl yet
            vcvars = VCVars(self)
            vcvars.generate()

    def _patch_sources(self):
        # Get the version of the current compiler instead of gcc
        linux_include = os.path.join(self.source_folder, "build", "linux.inc")
        replace_in_file(self, linux_include, "shell gcc", "shell $(CC)")
        replace_in_file(self, linux_include, "= gcc", "= $(CC)")
        if self.version != "2019_u9" and self.settings.build_type == "Debug":
            replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "release", "debug")
        for inc_file in glob.glob(os.path.join(self.source_folder, "build", "*.inc")):
            # Fix 'ar: two different operation options specified' due to unrecognized -m64 flag in 2020.04
            replace_in_file(self, inc_file, "LIB_LINK_FLAGS += -m64", "LIB_LINK_FLAGS += ", strict=False)

    def build(self):
        self._patch_sources()

        def add_flag(name, value):
            if name in os.environ:
                os.environ[name] += " " + value
            else:
                os.environ[name] = value

        with chdir(self, self.source_folder):
            # intentionally not using AutoToolsBuildEnvironment for now - it's broken for clang-cl
            if self._is_clanglc:
                add_flag("CFLAGS", "-mrtm")
                add_flag("CXXFLAGS", "-mrtm")

            autotools = Autotools(self)
            for target in ["tbb", "tbbmalloc", "tbbproxy"]:
                autotools.make(target)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include", "tbb", "compat"),
            src=os.path.join(self.source_folder, "include", "tbb", "compat"),
        )
        build_folder = os.path.join(self.source_folder, "build")
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        copy(
            self,
            pattern=f"*{build_type}*.lib",
            dst=os.path.join(self.package_folder, "lib"),
            src=build_folder,
            keep_path=False,
        )
        copy(
            self,
            pattern=f"*{build_type}*.a",
            dst=os.path.join(self.package_folder, "lib"),
            src=build_folder,
            keep_path=False,
        )
        copy(
            self,
            pattern=f"*{build_type}*.dll",
            dst=os.path.join(self.package_folder, "bin"),
            src=build_folder,
            keep_path=False,
        )
        copy(
            self,
            pattern=f"*{build_type}*.dylib",
            dst=os.path.join(self.package_folder, "lib"),
            src=build_folder,
            keep_path=False,
        )
        # Copy also .dlls to lib folder so consumers can link against them directly when using MinGW
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            copy(
                self,
                f"*{build_type}*.dll",
                dst=os.path.join(self.package_folder, "lib"),
                src=build_folder,
                keep_path=False,
            )

        if self.settings.os in ["Linux", "FreeBSD"]:
            extension = "so"
            if self.options.shared:
                copy(
                    self,
                    f"*{build_type}*.{extension}.*",
                    dst=os.path.join(self.package_folder, "lib"),
                    src=build_folder,
                    keep_path=False,
                )
                outputlibdir = os.path.join(self.package_folder, "lib")
                with chdir(self, outputlibdir):
                    for fpath in os.listdir(outputlibdir):
                        filepath = fpath[0 : fpath.rfind("." + extension) + len(extension) + 1]
                        self.run(f'ln -s "{fpath}" "{filepath}"')

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TBB")
        self.cpp_info.set_property("cmake_target_name", "TBB::TBB")

        suffix = "_debug" if self.settings.build_type == "Debug" else ""

        # tbb
        self.cpp_info.components["libtbb"].set_property("cmake_target_name", "TBB::tbb")
        self.cpp_info.components["libtbb"].libs = [f"tbb{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtbb"].system_libs = ["dl", "rt", "pthread"]

        # tbbmalloc
        if self.options.tbbmalloc:
            self.cpp_info.components["tbbmalloc"].set_property("cmake_target_name", "TBB::tbbmalloc")
            self.cpp_info.components["tbbmalloc"].libs = [f"tbbmalloc{suffix}"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["tbbmalloc"].system_libs = ["dl", "pthread"]

            # tbbmalloc_proxy
            if self.options.tbbproxy:
                self.cpp_info.components["tbbmalloc_proxy"].set_property("cmake_target_name", "TBB::tbbmalloc_proxy")
                self.cpp_info.components["tbbmalloc_proxy"].libs = [f"tbbmalloc_proxy{suffix}"]
                self.cpp_info.components["tbbmalloc_proxy"].requires = ["tbbmalloc"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        self.cpp_info.components["libtbb"].names["cmake_find_package"] = "tbb"
        self.cpp_info.components["libtbb"].names["cmake_find_package_multi"] = "tbb"
