from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.files import get, replace_in_file, save, chdir, copy
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conan.tools.scm import Version
from conans import tools as legacy_tools
import os
import textwrap

required_conan_version = ">=1.53.0"


class OneTBBConan(ConanFile):
    name = "onetbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = (
        "oneAPI Threading Building Blocks (oneTBB) lets you easily write parallel "
        "C++ programs that take full advantage of multicore performance, that "
        "are portable, composable and have future-proof scalability."
    )
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")

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
    def _source_subfolder(self):
        return "source_subfolder"

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

    def validate(self):
        if self.settings.os == "Macos":
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "8.0":
                raise ConanInvalidConfiguration("%s %s couldn't be built by apple-clang < 8.0" % (self.name, self.version))
        if not self.options.shared:
            self.output.warn("oneTBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and \
           (not self.options.shared or \
            not self.options.tbbmalloc):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmaloc and shared options")

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbproxy

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if "CONAN_MAKE_PROGRAM" not in os.environ and not legacy_tools.which("make"):
                self.tool_requires("make/4.2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        def add_flag(name, value):
            if name in os.environ:
                os.environ[name] += " " + value
            else:
                os.environ[name] = value

        # Get the version of the current compiler instead of gcc
        linux_include = os.path.join(self._source_subfolder, "build", "linux.inc")
        replace_in_file(self, linux_include, "shell gcc", "shell $(CC)")
        replace_in_file(self, linux_include, "= gcc", "= $(CC)")

        if self.version != "2019_u9" and self.settings.build_type == "Debug":
            replace_in_file(self, os.path.join(self._source_subfolder, "Makefile"), "release", "debug")

        if str(self._base_compiler) in ["Visual Studio", "msvc"]:
            save(self,
                os.path.join(self._source_subfolder, "build", "big_iron_msvc.inc"),
                # copy of big_iron.inc adapted for MSVC
                textwrap.dedent("""\
                    LIB_LINK_CMD = {}.exe
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
                """.format("xilib" if self.settings.compiler == "intel" else "lib"))
            )
            extra = "" if self.options.shared else "extra_inc=big_iron_msvc.inc"
        else:
            extra = "" if self.options.shared else "extra_inc=big_iron.inc"

        arch = {
            "x86": "ia32",
            "x86_64": "intel64",
            "armv7": "armv7",
            "armv8": "arm64"
            if (self.settings.os == "iOS" or self.settings.os == "Macos")
            else "aarch64",
        }[str(self.settings.arch)]
        extra += " arch=%s" % arch

        if self.settings.os == "iOS":
            extra += " target=ios"

        if str(self._base_compiler) in ("gcc", "clang", "apple-clang"):
            if str(self._base_compiler.libcxx) in ("libstdc++", "libstdc++11"):
                extra += " stdlib=libstdc++"
            elif str(self._base_compiler.libcxx) == "libc++":
                extra += " stdlib=libc++"

            if str(self.settings.compiler) == "intel":
                extra += " compiler=icc"
            elif str(self.settings.compiler) in ("clang", "apple-clang"):
                extra += " compiler=clang"
            else:
                extra += " compiler=gcc"

            if self.settings.os == "Linux":
                # runtime is supposed to track the version of the c++ stdlib,
                # the version of glibc, and the version of the linux kernel.
                # However, it isn't actually used anywhere other than for
                # logging and build directory names.
                # TBB computes the value of this variable using gcc, which we
                # don't necessarily want to require when building this recipe.
                # Setting it to a dummy value prevents TBB from calling gcc.
                extra += " runtime=gnu"
        elif str(self._base_compiler) in ["Visual Studio", "msvc"]:
            if "MT" in msvc_runtime_flag(self):
                runtime = "vc_mt"
            else:
                if self.settings.compiler == "Visual Studio":
                    runtime = {
                        "8": "vc8",
                        "9": "vc9",
                        "10": "vc10",
                        "11": "vc11",
                        "12": "vc12",
                        "14": "vc14",
                        "15": "vc14.1",
                        "16": "vc14.2"
                    }.get(str(self._base_compiler.version), "vc14.2")
                else:
                    runtime = {
                        "190": "vc14",
                        "191": "vc14.1",
                        "192": "vc14.2"
                    }.get(str(self._base_compiler.version), "vc14.2")
            extra += " runtime=%s" % runtime

            if self.settings.compiler == "intel":
                extra += " compiler=icl"
            else:
                extra += " compiler=cl"
        cxx_std_flag = legacy_tools.cppstd_flag(self.settings)
        if cxx_std_flag:
            cxx_std_value = (
                cxx_std_flag.split("=")[1]
                if "=" in cxx_std_flag
                else cxx_std_flag.split(":")[1]
                if ":" in cxx_std_flag
                else None
            )
            if cxx_std_value:
                extra += f" stdver={cxx_std_value}"

        make = legacy_tools.get_env("CONAN_MAKE_PROGRAM", legacy_tools.which("make") or legacy_tools.which("mingw32-make"))
        if not make:
            raise ConanException("This package needs 'make' in the path to build")

        with chdir(self, self._source_subfolder):
            # intentionally not using AutoToolsBuildEnvironment for now - it's broken for clang-cl
            if self._is_clanglc:
                add_flag("CFLAGS", "-mrtm")
                add_flag("CXXFLAGS", "-mrtm")

            targets = ["tbb", "tbbmalloc", "tbbproxy"]
            context = legacy_tools.no_op()
            if self.settings.compiler == "intel":
                context = legacy_tools.intel_compilervars(self)
            elif is_msvc(self):
                # intentionally not using vcvars for clang-cl yet
                context = legacy_tools.vcvars(self)
            with context:
                self.run("%s %s %s" % (make, extra, " ".join(targets)))

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._source_subfolder, "include"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include", "tbb", "compat"), src=os.path.join(self._source_subfolder, "include", "tbb", "compat"))
        build_folder = os.path.join(self._source_subfolder, "build")
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        copy(self, pattern=f"*{build_type}*.lib", dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)
        copy(self, pattern=f"*{build_type}*.a", dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)
        copy(self, pattern=f"*{build_type}*.dll", dst=os.path.join(self.package_folder, "bin"), src=build_folder, keep_path=False)
        copy(self, pattern=f"*{build_type}*.dylib", dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)
        # Copy also .dlls to lib folder so consumers can link against them directly when using MinGW
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            copy(self, f"*{build_type}*.dll", dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)

        if self.settings.os == "Linux":
            extension = "so"
            if self.options.shared:
                copy(self, f"*{build_type}*.{extension}.*", dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)
                outputlibdir = os.path.join(self.package_folder, "lib")
                with chdir(self, outputlibdir):
                    for fpath in os.listdir(outputlibdir):
                        filepath = fpath[0:fpath.rfind("." + extension) + len(extension) + 1]
                        self.run(f'ln -s "{fpath}" "{filepath}"', run_environment=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TBB")

        suffix = "_debug" if self.settings.build_type == "Debug" else ""

        # tbb
        self.cpp_info.components["libtbb"].set_property("cmake_target_name", "TBB::tbb")
        self.cpp_info.components["libtbb"].libs = ["tbb{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtbb"].system_libs = ["dl", "rt", "pthread"]

        # tbbmalloc
        if self.options.tbbmalloc:
            self.cpp_info.components["tbbmalloc"].set_property("cmake_target_name", "TBB::tbbmalloc")
            self.cpp_info.components["tbbmalloc"].libs = ["tbbmalloc{}".format(suffix)]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["tbbmalloc"].system_libs = ["dl", "pthread"]

            # tbbmalloc_proxy
            if self.options.tbbproxy:
                self.cpp_info.components["tbbmalloc_proxy"].set_property("cmake_target_name", "TBB::tbbmalloc_proxy")
                self.cpp_info.components["tbbmalloc_proxy"].libs = ["tbbmalloc_proxy{}".format(suffix)]
                self.cpp_info.components["tbbmalloc_proxy"].requires = ["tbbmalloc"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        self.cpp_info.components["libtbb"].names["cmake_find_package"] = "tbb"
        self.cpp_info.components["libtbb"].names["cmake_find_package_multi"] = "tbb"
