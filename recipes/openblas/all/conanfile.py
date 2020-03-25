from conans import ConanFile, CMake, tools
import sys
import os


class OpenBLAS(ConanFile):
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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_lapack": False,
        "use_thread": True,
        "dynamic_arch": False
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def system_requirements(self):
        if self.options.build_lapack and tools.os_info.is_linux:
            installer = tools.SystemPackageTool()
            if tools.os_info.linux_distro == "arch":
                # In Arch Linux the name of the package containing the Fortran
                # compiler is gcc-fortran
                installer.install("gcc-fortran")
            else:
                # In other dists try installing a package with name gfortran
                # (this works in ubuntu and might or might not work in other
                # distros)
                installer.install("gfortran")

                # It seems that just gfortan is not enough in ubuntu. We need
                # to install a libgfortan-X-dev package, where X must match gcc
                # version.
                if self.settings.get_safe("compiler") == "gcc":
                    if self.settings.get_safe("compiler.version") == "8":
                        installer.install("libgfortran-8-dev")
                    elif self.settings.get_safe("compiler.version") == "7":
                        installer.install("libgfortran-7-dev")
                    elif self.settings.get_safe("compiler.version") == "9":
                        installer.install("libgfortran-9-dev")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('OpenBLAS-{}'.format(self.version), self._source_subfolder)

    def _create_cmake_helper(self):
        cmake = CMake(self)
        if self.options.build_lapack:
            self.output.warn(
                "Building with lapack support requires a Fortran compiler.")

        cmake.definitions["NOFORTRAN"] = not self.options.build_lapack
        cmake.definitions["BUILD_WITHOUT_LAPACK"] = not self.options.build_lapack
        cmake.definitions["DYNAMIC_ARCH"] = self.options.dynamic_arch
        cmake.definitions["USE_THREAD"] = self.options.use_thread

        if not self.options.use_thread:
            # Required for safe concurrent calls to OpenBLAS routines
            cmake.definitions["USE_LOCKING"] = True

        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            cmake.definitions["MSVC_STATIC_CRT"] = True

        if self.settings.os == "Linux":
            # This is a workaround to add the libm dependency on linux,
            # which is required to successfully compile on older gcc versions.
            cmake.definitions["ANDROID"] = True

        return cmake

    def build(self):
        cmake = self._create_cmake_helper()
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy(
            pattern="LICENSE",
            dst="licenses",
            src=self._source_subfolder)
        cmake = self._create_cmake_helper()
        cmake.install(build_dir=self._build_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.env_info.OpenBLAS_HOME = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.use_thread:
                self.cpp_info.system_libs = ["pthread"]

            if self.options.build_lapack:
                self.cpp_info.system_libs.append("gfortran")
        self.cpp_info.names["cmake_find_package"] = "OpenBLAS"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenBLAS"
        self.cpp_info.names['pkg_config'] = "OpenBLAS"
