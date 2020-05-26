from conans import ConanFile, CMake, tools
import os
import shutil


class FreetypeConan(ConanFile):
    name = "freetype"

    _libtool_version = "23.0.17"  # check docs/version.txt, this is a different version mumber!
    description = "FreeType is a freely available software library to render fonts."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freetype.org"
    license = "FTL"
    topics = ("conan", "freetype", "fonts")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'with_png': True,
        'with_zlib': True,
        'with_bzip2': True
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('{0}-{1}'.format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PROJECT_VERSION"] = self._libtool_version
        cmake.definitions["FT_WITH_ZLIB"] = self.options.with_zlib
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ZLIB"] = not self.options.with_zlib
        cmake.definitions["FT_WITH_PNG"] = self.options.with_png
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = not self.options.with_png
        cmake.definitions["FT_WITH_BZIP2"] = self.options.with_bzip2
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_BZip2"] = not self.options.with_bzip2
        # TODO: Harfbuzz can be added as an option as soon as it is available.
        cmake.definitions["FT_WITH_HARFBUZZ"] = False
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_HarfBuzz"] = True
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _make_freetype_config(self):
        freetype_config_in = os.path.join(self._source_subfolder, "builds", "unix", "freetype-config.in")
        if not os.path.isdir(os.path.join(self.package_folder, "bin")):
            os.makedirs(os.path.join(self.package_folder, "bin"))
        freetype_config = os.path.join(self.package_folder, "bin", "freetype-config")
        shutil.copy(freetype_config_in, freetype_config)
        libs = "-lfreetyped" if self.settings.build_type == "Debug" else "-lfreetype"
        staticlibs = "-lm %s" % libs if self.settings.os == "Linux" else libs
        tools.replace_in_file(freetype_config, r"%PKG_CONFIG%", r"/bin/false")  # never use pkg-config
        tools.replace_in_file(freetype_config, r"%prefix%", r"$conan_prefix")
        tools.replace_in_file(freetype_config, r"%exec_prefix%", r"$conan_exec_prefix")
        tools.replace_in_file(freetype_config, r"%includedir%", r"$conan_includedir")
        tools.replace_in_file(freetype_config, r"%libdir%", r"$conan_libdir")
        tools.replace_in_file(freetype_config, r"%ft_version%", r"$conan_ftversion")
        tools.replace_in_file(freetype_config, r"%LIBSSTATIC_CONFIG%", r"$conan_staticlibs")
        tools.replace_in_file(freetype_config, r"-lfreetype", libs)
        tools.replace_in_file(freetype_config, r"export LC_ALL", """export LC_ALL
BINDIR=$(dirname $0)
conan_prefix=$(dirname $BINDIR)
conan_exec_prefix=${{conan_prefix}}/bin
conan_includedir=${{conan_prefix}}/include
conan_libdir=${{conan_prefix}}/lib
conan_ftversion={version}
conan_staticlibs="{staticlibs}"
""".format(version=self._libtool_version, staticlibs=staticlibs))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self._make_freetype_config()
        self.copy("FTL.TXT", dst="licenses", src=os.path.join(self._source_subfolder, "docs"))
        self.copy("GPLv2.TXT", dst="licenses", src=os.path.join(self._source_subfolder, "docs"))
        self.copy("LICENSE.TXT", dst="licenses", src=os.path.join(self._source_subfolder, "docs"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.includedirs.append(os.path.join("include", "freetype2"))
        freetype_config = os.path.join(self.package_folder, "bin", "freetype-config")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.FT2_CONFIG = freetype_config
        self.user_info.LIBTOOL_VERSION = self._libtool_version
        self._chmod_plus_x(freetype_config)
        self.cpp_info.names['cmake_find_package'] = 'Freetype'
        self.cpp_info.names['cmake_find_package_multi'] = 'Freetype'
        self.cpp_info.names['pkg_config'] = 'freetype2'
