from conans import ConanFile, CMake, tools
import os
import shutil
import textwrap

required_conan_version = ">=1.33.0"


class FreetypeConan(ConanFile):
    name = "freetype"

    _libtool_version = "23.0.17"  # check docs/version.txt, this is a different version mumber!
    description = "FreeType is a freely available software library to render fonts."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freetype.org"
    license = "FTL"
    topics = ("conan", "freetype", "fonts")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_brotli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_zlib": True,
        "with_bzip2": True,
        "with_brotli": True
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_with_brotli_option(self):
        return tools.Version(self.version) >= "2.10.2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_with_brotli_option:
            del self.options.with_brotli

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/1.0.9")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{0}-{1}".format(self.name, self.version), self._source_subfolder)

    def _patch_sources(self):
        # Do not accidentally enable dependencies we have disabled
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        find_harfbuzz = "find_package(HarfBuzz {})".format("1.3.0" if tools.Version(self.version) < "2.10.2" else "${HARFBUZZ_MIN_VERSION}")
        tools.replace_in_file(cmakelists, find_harfbuzz, "")
        tools.replace_in_file(cmakelists, "if (HARFBUZZ_FOUND)", "if(0)")
        if not self.options.with_png:
            tools.replace_in_file(cmakelists, "find_package(PNG)", "")
            tools.replace_in_file(cmakelists, "if (PNG_FOUND)", "if(0)")
        if not self.options.with_zlib:
            tools.replace_in_file(cmakelists, "find_package(ZLIB)", "")
            tools.replace_in_file(cmakelists, "if (ZLIB_FOUND)", "if(0)")
        if not self.options.with_bzip2:
            tools.replace_in_file(cmakelists, "find_package(BZip2)", "")
            tools.replace_in_file(cmakelists, "if (BZIP2_FOUND)", "if(0)")
        if self._has_with_brotli_option:
            # the custom FindBrotliDec of upstream is too fragile
            tools.replace_in_file(cmakelists,
                                  "find_package(BrotliDec REQUIRED)",
                                  "find_package(Brotli REQUIRED)\n"
                                  "set(BROTLIDEC_FOUND 1)\n"
                                  "set(BROTLIDEC_LIBRARIES \"Brotli::Brotli\")")
            if not self.options.with_brotli:
                tools.replace_in_file(cmakelists, "find_package(BrotliDec)", "")
                tools.replace_in_file(cmakelists, "if (BROTLIDEC_FOUND)", "if(0)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PROJECT_VERSION"] = self._libtool_version
        self._cmake.definitions["FT_WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["FT_WITH_PNG"] = self.options.with_png
        self._cmake.definitions["FT_WITH_BZIP2"] = self.options.with_bzip2
        # TODO: Harfbuzz can be added as an option as soon as it is available.
        self._cmake.definitions["FT_WITH_HARFBUZZ"] = False
        if self._has_with_brotli_option:
            self._cmake.definitions["FT_WITH_BROTLI"] = self.options.with_brotli
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
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

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "freetype": "Freetype::Freetype",
            }
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
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
        # cmake's FindFreetype.cmake module with imported target: Freetype::Freetype
        self.cpp_info.names["cmake_find_package"] = "Freetype"
        self.cpp_info.filenames["cmake_find_package_multi"] = "freetype"
        self.cpp_info.names["cmake_find_package_multi"] = "Freetype"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "freetype2"
