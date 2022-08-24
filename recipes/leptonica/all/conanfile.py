from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class LeptonicaConan(ConanFile):
    name = "leptonica"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Library containing software that is broadly useful for " \
                  "image processing and image analysis applications."
    topics = ("leptonica", "image", "multimedia", "format", "graphics")
    homepage = "http://leptonica.org"
    license = "BSD 2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_gif": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_openjpeg": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_gif": True,
        "with_jpeg": True,
        "with_png": True,
        "with_tiff": True,
        "with_openjpeg": True,
        "with_webp": True,
    }

    generators = "cmake", "cmake_find_package", "pkg_config"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")

    def build_requirements(self):
        if self.options.with_webp or self.options.with_openjpeg:
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        cmakelists_src = os.path.join(self._source_subfolder, "src", "CMakeLists.txt")
        cmake_configure = os.path.join(self._source_subfolder, "cmake", "Configure.cmake")

        # Fix installation
        tools.replace_in_file(cmakelists_src, "${CMAKE_BINARY_DIR}", "${PROJECT_BINARY_DIR}")

        # Honor options and inject dependencies definitions
        # TODO: submit a patch upstream
        ## zlib
        tools.replace_in_file(cmakelists_src, "${ZLIB_LIBRARIES}", "ZLIB::ZLIB")
        if not self.options.with_zlib:
            tools.replace_in_file(cmakelists_src, "if (ZLIB_LIBRARIES)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (ZLIB_FOUND)", "if(0)")
        ## giflib
        tools.replace_in_file(cmakelists_src, "${GIF_LIBRARIES}", "GIF::GIF")
        if not self.options.with_gif:
            tools.replace_in_file(cmakelists_src, "if (GIF_LIBRARIES)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (GIF_FOUND)", "if(0)")
        ## libjpeg
        tools.replace_in_file(cmakelists_src, "${JPEG_LIBRARIES}", "JPEG::JPEG")
        if not self.options.with_jpeg:
            tools.replace_in_file(cmakelists_src, "if (JPEG_LIBRARIES)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (JPEG_FOUND)", "if(0)")
        ## libpng
        tools.replace_in_file(cmakelists_src, "${PNG_LIBRARIES}", "PNG::PNG")
        if not self.options.with_png:
            tools.replace_in_file(cmakelists_src, "if (PNG_LIBRARIES)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (PNG_FOUND)", "if(0)")
        ## libtiff
        tools.replace_in_file(cmakelists_src, "${TIFF_LIBRARIES}", "TIFF::TIFF")
        if not self.options.with_tiff:
            tools.replace_in_file(cmakelists_src, "if (TIFF_LIBRARIES)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (TIFF_FOUND)", "if(0)")
        ## We have to be more aggressive with dependencies found with pkgconfig
        ## Injection of libdirs is ensured by conan_basic_setup()
        ## openjpeg
        tools.replace_in_file(cmakelists, "if(NOT JP2K)", "if(0)")
        tools.replace_in_file(cmakelists_src,
                              "if (JP2K_FOUND)",
                              "if (JP2K_FOUND)\n"
                              "target_compile_definitions(leptonica PRIVATE ${JP2K_CFLAGS_OTHER})")
        if not self.options.with_openjpeg:
            tools.replace_in_file(cmakelists_src, "if (JP2K_FOUND)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (JP2K_FOUND)", "if(0)")
        ## libwebp
        tools.replace_in_file(cmakelists, "if(NOT WEBP)", "if(0)")
        tools.replace_in_file(cmakelists_src,
                              "if (WEBP_FOUND)",
                              "if (WEBP_FOUND)\n"
                              "target_compile_definitions(leptonica PRIVATE ${WEBP_CFLAGS_OTHER} ${WEBPMUX_CFLAGS_OTHER})")
        tools.replace_in_file(cmakelists_src, "${WEBP_LIBRARIES}", "${WEBP_LIBRARIES} ${WEBPMUX_LIBRARIES}")
        if tools.Version(self.version) >= "1.79.0":
            tools.replace_in_file(cmakelists, "if(NOT WEBPMUX)", "if(0)")
        if not self.options.with_webp:
            tools.replace_in_file(cmakelists_src, "if (WEBP_FOUND)", "if(0)")
            tools.replace_in_file(cmake_configure, "if (WEBP_FOUND)", "if(0)")

        # Remove detection of fmemopen() on macOS < 10.13
        # CheckFunctionExists will find it in the link library.
        # There's no error because it's not including the header with the
        # deprecation macros.
        if self.settings.os == "Macos" and self.settings.os.version:
            if tools.Version(self.settings.os.version) < "10.13":
                tools.replace_in_file(cmake_configure,
                                      "set(functions_list\n    "
                                      "fmemopen\n    fstatat\n)",
                                      "set(functions_list\n    "
                                      "fstatat\n)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) < "1.79.0":
            self._cmake.definitions["STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_PROG"] = False
        self._cmake.definitions["SW_BUILD"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="leptonica-license.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))  # since 1.81.0
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"leptonica": "Leptonica::Leptonica"}
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Leptonica")
        self.cpp_info.set_property("cmake_target_name", "leptonica")
        self.cpp_info.set_property("pkg_config_name", "lept")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs.append(os.path.join("include", "leptonica"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Leptonica"
        self.cpp_info.names["cmake_find_package_multi"] = "Leptonica"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "lept"
