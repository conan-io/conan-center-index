import os
from conans import ConanFile, tools, CMake
from conan.tools.files import rename, apply_conandata_patches


class CycloneDDSConan(ConanFile):

    name = "cyclonedds"
    license = "Eclipse Public License - v 2.0"
    description = "Eclipse Cyclone DDS project"
    homepage = 'https://github.com/eclipse-cyclonedds/cyclonedds'
    url = "https://github.com/conan-io/conan-center-index"
    topics = "dds", "ros2"

    options = {
        "enable_ssl": [True, False],
        "enable_security": [True, False],
        "enable_lifespan": [True, False],
        "enable_deadline_missed": [True, False],
        "enable_type_discovery": [True, False],
        "shared": [False, True],
        "fPIC": [False, True]
    }
    default_options = {
        "enable_ssl": False,
        "enable_security": True,
        "enable_lifespan": True,
        "enable_deadline_missed": True,
        "enable_type_discovery": True,
        "fPIC": True,
        "shared": False
    }

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ("patches/**", )

    build_requires = "bison/3.7.1"
    generators = "cmake"

    _cmake = None
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.enable_ssl:
            self.requires("openssl/1.1.1c")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        downloaded_folder_name = "{}-{}".format(self.name, self.version)
        rename(self, downloaded_folder_name, self._source_subfolder)

        return

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        # # set_cmake_flags is necessary to cross-build from 64bit to 32bit on linux
        # cmake = CMake(self, set_cmake_flags=True, append_vcvars=True)
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SSL"] = self.options.enable_ssl
        self._cmake.definitions["ENABLE_SECURITY"] = self.options.enable_security
        self._cmake.definitions["ENABLE_LIFESPAN"] = self.options.enable_lifespan
        self._cmake.definitions["ENABLE_DEADLINE_MISSED"] = self.options.enable_deadline_missed
        self._cmake.definitions["ENABLE_TYPE_DISCOVERY"] = self.options.enable_type_discovery
        # Don't include the CMakeCPack.cmake file since we are not building an installer
        self._cmake.definitions['CMAKECPACK_INCLUDED'] = 'TRUE'
        self._cmake.definitions["BUILD_IDLC"] = True

        # # Workaround for an annoying behavior of the vcvarsall and the helper in Conan
        # # vcvarsall also adds CMake and Ninja to the path but by default at the end. The
        # # Conan helper detects which directories were added (but not whether they were added at the beginning or the end)
        # # To prevent CMake version 3.12 from VS 2017 being found we use `append_vcvars=True`. However this causes CMake
        # # to find clang instead of msvc. To force discovery of msvc we explicitly set CMAKE_<LANG>_COMPILER
        # if self._is_windows_os_and_msvc_compiler():
        #     cmake.definitions["CMAKE_C_COMPILER"] = "cl"
        #     cmake.definitions["CMAKE_CXX_COMPILER"] = "cl"

        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        apply_conandata_patches(self)

        assert self.install_folder == self.build_folder, "Build and install folders must be the same"
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="NOTICE.md", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.names['cmake_find_package'] = "CycloneDDS"
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.build_modules['cmake_find_package'] = [
            os.path.join('lib', 'cmake', 'CycloneDDS', 'idlc', 'Generate.cmake')
        ]

        self.env_info.LD_LIBRARY_PATH.extend(
            [os.path.join(self.package_folder, x) for x in self.cpp_info.libdirs])
        self.env_info.PATH.extend(
            [os.path.join(self.package_folder, x) for x in self.cpp_info.bindirs])
