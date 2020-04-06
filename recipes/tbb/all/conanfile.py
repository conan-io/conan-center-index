import os
from conans import ConanFile, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration


class TBBConan(ConanFile):
    name = "tbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = """Intel Threading Building Blocks (Intel TBB) lets you easily write parallel C++
programs that take full advantage of multicore performance, that are portable and composable, and
that have future-proof scalability"""
    topics = ("conan", "tbb", "threading", "parallelism", "tbbmalloc")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "tbbmalloc": [True, False], "tbbproxy": [True, False]}
    default_options = {"shared": True, "fPIC": True, "tbbmalloc": False, "tbbproxy": False}
    _source_subfolder = "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_MAKE_PROGRAM" not in os.environ and not tools.which("make"):
                self.build_requires("make/4.2.1")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Macos" and \
           self.settings.compiler == "apple-clang" and \
           Version(self.settings.compiler.version.value) < "8.0":
            raise ConanInvalidConfiguration("%s %s couldn't be built by apple-clang < 8.0" % (self.name, self.version))
        if not self.options.shared:
            self.output.warn("Intel-TBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and \
           (not self.options.shared or \
            not self.options.tbbmalloc):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmaloc and shared options")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def _is_mingw(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    @property
    def _is_clanglc(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("one{}-{}".format(self.name.upper(), self.version.upper()), self._source_subfolder)

        # Get the version of the current compiler instead of gcc
        linux_include = os.path.join(self._source_subfolder, "build", "linux.inc")
        tools.replace_in_file(linux_include, "shell gcc", "shell $(CC)")
        tools.replace_in_file(linux_include, "= gcc", "= $(CC)")

    def _get_targets(self):
        targets = ["tbb"]
        if self.options.tbbmalloc:
            targets.append("tbbmalloc")
        if self.options.tbbproxy:
            targets.append("tbbproxy")
        return targets

    def build(self):
        def add_flag(name, value):
            if name in os.environ:
                os.environ[name] += ' ' + value
            else:
                os.environ[name] = value

        if self.version != "2019_u9" and self.settings.build_type == "Debug":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"), "release", "debug")

        if self._is_msvc:
            tools.save(os.path.join(self._source_subfolder, "build", "big_iron_msvc.inc"),
                       # copy of big_iron.inc adapted for MSVC
                       """
LIB_LINK_CMD = lib.exe
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
""")
            extra = "" if self.options.shared else "extra_inc=big_iron_msvc.inc"
        else:
            extra = "" if self.options.shared else "extra_inc=big_iron.inc"
        arch = {"x86": "ia32",
                "x86_64": "intel64",
                "armv7":  "armv7",
                "armv8": "aarch64"}.get(str(self.settings.arch))
        if self.settings.compiler in ['gcc', 'clang', 'apple-clang']:
            if str(self.settings.compiler.libcxx) in ['libstdc++', 'libstdc++11']:
                extra += " stdlib=libstdc++"
            elif str(self.settings.compiler.libcxx) == 'libc++':
                extra += " stdlib=libc++"
            extra += " compiler=gcc" if self.settings.compiler == 'gcc' else " compiler=clang"

            extra += " gcc_version={}".format(str(self.settings.compiler.version))
        make = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which('mingw32-make'))
        if not make:
            raise ConanInvalidConfiguration("This package needs 'make' in the path to build")

        with tools.chdir(self._source_subfolder):
            # intentionally not using AutoToolsBuildEnvironment for now - it's broken for clang-cl
            if self._is_clanglc:
                add_flag('CFLAGS', '-mrtm')
                add_flag('CXXFLAGS', '-mrtm')

            targets = ["tbb", "tbbmalloc", "tbbproxy"]
            if self._is_msvc:
                # intentionally not using vcvars for clang-cl yet
                with tools.vcvars(self.settings):
                    if self.settings.get_safe("compiler.runtime") in ["MT", "MTd"]:
                        runtime = "vc_mt"
                    else:
                        runtime = {"8": "vc8",
                                   "9": "vc9",
                                   "10": "vc10",
                                   "11": "vc11",
                                   "12": "vc12",
                                   "14": "vc14",
                                   "15": "vc14.1",
                                   "16": "vc14.2"}.get(str(self.settings.compiler.version), "vc14.2")
                    self.run("%s arch=%s runtime=%s %s %s" % (make, arch, runtime, extra, " ".join(targets)))
            elif self._is_mingw:
                self.run("%s arch=%s compiler=gcc %s %s" % (make, arch, extra, " ".join(targets)))
            else:
                self.run("%s arch=%s %s %s" % (make, arch, extra, " ".join(targets)))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src="%s/include" % self._source_subfolder)
        self.copy(pattern="*", dst="include/tbb/compat", src="%s/include/tbb/compat" % self._source_subfolder)
        build_folder = "%s/build/" % self._source_subfolder
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        self.copy(pattern="*%s*.lib" % build_type, dst="lib", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.a" % build_type, dst="lib", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.dll" % build_type, dst="bin", src=build_folder, keep_path=False)
        self.copy(pattern="*%s*.dylib" % build_type, dst="lib", src=build_folder, keep_path=False)
        # Copy also .dlls to lib folder so consumers can link against them directly when using MinGW
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.copy("*%s*.dll" % build_type, dst="lib", src=build_folder, keep_path=False)

        if self.settings.os == "Linux":
            extension = "so"
            if self.options.shared:
                self.copy("*%s*.%s.*" % (build_type, extension), "lib", build_folder,
                          keep_path=False)
                outputlibdir = os.path.join(self.package_folder, "lib")
                os.chdir(outputlibdir)
                for fpath in os.listdir(outputlibdir):
                    self.run("ln -s \"%s\" \"%s\"" %
                             (fpath, fpath[0:fpath.rfind("." + extension) + len(extension) + 1]))

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbmalloc_proxy

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        suffix = "_debug" if self.settings.build_type == "Debug" else ""
        libs = {"tbb": "tbb", "tbbproxy": "tbbmalloc_proxy", "tbbmalloc": "tbbmalloc"}
        targets = self._get_targets()
        self.cpp_info.libs = ["{}{}".format(libs[target], suffix) for target in targets]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "rt", "m", "pthread"])
