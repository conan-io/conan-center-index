from conans import ConanFile, CMake, tools
import os
import shutil
import glob


class LibX265Conan(ConanFile):
    name = "libx265"
    homepage = "http://x265.org"
    topics = ("conan", "libx265", "codec", "video", "H.265")
    url = "https://github.com/conan-io/conan-center-index"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    license = "https://bitbucket.org/multicoreware/x265/src/default/COPYING"  # GPL-2.0-only + commercial
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "bit_depth": [8, 10, 12], "HDR10": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'bit_depth': '8', 'HDR10': False}
    generators = ['cmake']
    build_requires = "nasm/2.13.02", "ninja/1.9.0"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'x265_%s' % self.version
        os.rename(extracted_dir, "sources")

    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['ENABLE_LIBNUMA'] = False
        if self.settings.os == "Macos":
            cmake.definitions['CMAKE_SHARED_LINKER_FLAGS'] = '-Wl,-read_only_relocs,suppress'
        if self.settings.os != 'Windows':
            cmake.definitions['ENABLE_PIC'] = self.options.fPIC
        cmake.definitions['HIGH_BIT_DEPTH'] = self.options.bit_depth != 8
        cmake.definitions['MAIN12'] = self.options.bit_depth == 12
        cmake.definitions['ENABLE_HDR10_PLUS'] = self.options.HDR10
        if self.settings.os == "Linux":
            cmake.definitions["PLATFORM_LIBS"] = "dl"
        cmake.configure()
        return cmake

    def build(self):
        with tools.vcvars(self.settings, filter_known_paths=False):
            if self.settings.os == 'Windows':
                tools.replace_in_file(os.path.join('sources', 'source', 'CMakeLists.txt'),
                                    '${PROJECT_BINARY_DIR}/Debug/x265.pdb',
                                    '${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/x265.pdb')
                tools.replace_in_file(os.path.join('sources', 'source', 'CMakeLists.txt'),
                                    '${PROJECT_BINARY_DIR}/x265.pdb',
                                    '${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/x265.pdb')
            elif self.settings.os == "Android":
                tools.replace_in_file(os.path.join('sources', 'source', 'CMakeLists.txt'),
                    "list(APPEND PLATFORM_LIBS pthread)", "")
                tools.replace_in_file(os.path.join('sources', 'source', 'CMakeLists.txt'),
                    "list(APPEND PLATFORM_LIBS rt)", "")
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        with tools.vcvars(self.settings, filter_known_paths=False):
            cmake = self._configure_cmake()
            cmake.install()
        self.copy(pattern="COPYING", src='sources', dst='licenses')
        if self.settings.compiler == 'Visual Studio':
            for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.unlink(pdb_file)
            name = 'libx265.lib' if self.options.shared else 'x265-static.lib'
            shutil.move(os.path.join(self.package_folder, 'lib', name),
                        os.path.join(self.package_folder, 'lib', 'x265.lib'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = ['x265']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['dl', 'pthread', 'm'])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(['dl', 'm'])
        self.cpp_info.names['pkg_config'] = 'x265'
