from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class OpenblasConan(ConanFile):
    name = "openblas"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openblas.net"
    description = "An optimized BLAS library based on GotoBLAS2 1.13 BSD version"
    topics = (
        "openblas",
        "blas",
        "lapack"
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_lapack": [True, False],
        "use_thread": [True, False],
        "dynamic_arch": [True, False],
        "target": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": True,
        "use_thread": True,
        "dynamic_arch": True,
        "target": None
    }
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def _get_make_arch(self):
        return "32" if self.settings.arch == "x86" else "64"

    def _get_make_build_type_debug(self):
        return "0" if self.settings.build_type == "Release" else "1"

    @staticmethod
    def _get_make_option_value(option):
        return "1" if option else "0"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_apple_clang(self):
        return self.settings.compiler == "apple-clang"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('OpenBLAS-{}'.format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20200517")

    def _patch_sources(self):
        if self.version in self.conan_data.get("patches", ""):
            for patch in self.conan_data["patches"][self.version]:
                if "apple_clang" in patch["patch_file"] and not self._is_apple_clang:
                    continue
                tools.patch(**patch)
        
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.install"),
                              "OPENBLAS_INCLUDE_DIR := $(PREFIX)/include",
                              "OPENBLAS_INCLUDE_DIR := $(PREFIX)/include/openblas")
        
        # This is needed to avoid undefined sprintf symbols when using with msvc
        if self._is_msvc and tools.Version(self.settings.compiler.version):
            tools.replace_in_file(os.path.join(self._source_subfolder, "common.h"),
                                  "#if !defined(_MSC_VER)",
                                  "#define snprintf _snprintf\n#if !defined(_MSC_VER)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.build_lapack:
            self.output.warn("Building with lapack support requires a Fortran compiler.")

        self._cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        self._cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        self._cmake.definitions["DYNAMIC_ARCH"] = self.options.dynamic_arch
        self._cmake.definitions["USE_THREAD"] = self.options.use_thread

        # Required for safe concurrent calls to OpenBLAS routines
        self._cmake.definitions["USE_LOCKING"] = not self.options.use_thread

        self._cmake.definitions["MSVC_STATIC_CRT"] = False # don't, may lie to consumer, /MD or /MT is managed by conan

        # This is a workaround to add the libm dependency on linux,
        # which is required to successfully compile on older gcc versions.
        self._cmake.definitions["ANDROID"] = self.settings.os in ["Linux", "Android"]

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _build_cmake(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _install_msys2_package(self, package_name):
        try:
            self.run('bash -l -c "pacman -Qi {} > /dev/null"'.format(package_name))
        except ConanException:
            self.run('bash -l -c "pacman -S {} --noconfirm"'.format(package_name))

    def _build_make(self, args=None):
        if tools.os_info.is_windows:
            prefix = "mingw-w64-i686" if self.settings.arch == "x86" else "mingw-w64-x86_64"
            self._install_msys2_package("{}-gcc".format(prefix))
            self._install_msys2_package("{}-gcc-fortran".format(prefix))

        make_options = ["DEBUG={}".format(self._get_make_build_type_debug()),
                        "NO_SHARED={}".format(self._get_make_option_value(not self.options.shared)),
                        "BINARY={}".format(self._get_make_arch()),
                        "USE_THREAD={}".format(self._get_make_option_value(self.options.use_thread)),
                        "USE_LOCKING={}".format(self._get_make_option_value(not self.options.use_thread)),
                        "BUILD_WITHOUT_LAPACK={}".format(self._get_make_option_value(not self.options.build_lapack)),
                        "NOFORTRAN={}".format(self._get_make_option_value(not self.options.build_lapack)),
                        "DYNAMIC_ARCH={}".format(self._get_make_option_value(self.options.dynamic_arch))]

        # https://github.com/xianyi/OpenBLAS/wiki/How-to-build-OpenBLAS-for-Android
        target_android = {"armv6": "ARMV6",
                          "armv7": "ARMV7",
                          "armv7hf": "ARMV7",
                          "armv8": "ARMV8",
                          "sparc": "SPARC"}.get(str(self.settings.arch))

        target = target_android if self.options.target is None else self.options.target
        if tools.cross_building(self.settings):
            if "CC_FOR_BUILD" in os.environ:
                hostcc = os.environ["CC_FOR_BUILD"]
            else:
                hostcc = tools.which("cc") or tools.which("gcc") or tools.which("clang")
            make_options.append("HOSTCC={}".format(hostcc))

        if target:
            make_options.append("TARGET={}".format(target))

        if "CC" in os.environ:
            make_options.append("CC={}".format(os.environ["CC"]))

        if "AR" in os.environ:
            make_options.append("AR={}".format(os.environ["AR"]))

        use_win_bash = False
        if tools.os_info.is_windows:
            make_options.append("LIBNAME=openblas.lib")
            make_options.append("CC=${MINGW_PREFIX}/bin/gcc")
            make_options.append("FC=${MINGW_PREFIX}/bin/gfortran")
            use_win_bash = True
       
        if args:
            make_options.extend(args)

        self.run("cd {} && make {}".format(self._source_subfolder, ' '.join(make_options)), cwd=self.source_folder, win_bash=use_win_bash)

    def build(self):
        self._patch_sources()
        self._build_make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self._build_make(args=["PREFIX={}".format(tools.unix_path(self.package_folder)), 'install'])
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))       
 
    def package_info(self):
        self.env_info.OpenBLAS_HOME = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.use_thread:
                self.cpp_info.system_libs.append("pthread")
            if self.options.build_lapack:
                self.cpp_info.system_libs.append("gfortran")
        if self._is_msvc and tools.Version(self.settings.compiler.version) >= "14":
            self.cpp_info.system_libs.append("legacy_stdio_definitions")
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.names['pkg_config'] = "OpenBLAS"
