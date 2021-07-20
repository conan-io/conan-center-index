from conans import CMake, ConanFile, tools
import os
import shutil

required_conan_version = ">=1.33.0"


class Libx265Conan(ConanFile):
    name = "libx265"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    topics = ("conan", "libx265", "codec", "video", "H.265")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x265.html"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    license = ("GPL-2.0-only", "commercial")  # https://bitbucket.org/multicoreware/x265/src/default/COPYING
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "assembly": [True, False],
        "bit_depth": [8, 10, 12],
        "HDR10": [True, False],
        "SVG_HEVC_encoder": [True, False],
        "with_numa": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "assembly": True,
        "bit_depth": 8,
        "HDR10": False,
        "SVG_HEVC_encoder": False,
        "with_numa": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_numa
        # FIXME: Disable assembly by default if host is arm and compiler apple-clang for the moment.
        # Indeed, apple-clang is not able to understand some asm instructions of libx265
        if self.settings.compiler == "apple-clang" and "arm" in self.settings.arch:
            self.options.assembly = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.get_safe("with_numa", False):
            self.requires("libnuma/2.0.14")

    def build_requirements(self):
        if self.options.assembly:
            if self.settings.arch in ["x86", "x86_64"]:
                self.build_requires("nasm/2.15.05")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["ENABLE_ASSEMBLY"] = self.options.assembly
        self._cmake.definitions["ENABLE_LIBNUMA"] = self.options.get_safe("with_numa", False)
        if self.settings.os == "Macos":
            self._cmake.definitions["CMAKE_SHARED_LINKER_FLAGS"] = "-Wl,-read_only_relocs,suppress"
        self._cmake.definitions["HIGH_BIT_DEPTH"] = self.options.bit_depth != 8
        self._cmake.definitions["MAIN12"] = self.options.bit_depth == 12
        self._cmake.definitions["ENABLE_HDR10_PLUS"] = self.options.HDR10
        self._cmake.definitions["ENABLE_SVT_HEVC"] = self.options.SVG_HEVC_encoder
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["STATIC_LINK_CRT"] = "T" in str(self.settings.compiler.runtime)
        if self.settings.os == "Linux":
            self._cmake.definitions["PLATFORM_LIBS"] = "dl"
        if tools.cross_building(self.settings):
            # FIXME: too specific and error prone, should be delegated to CMake helper
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            self._cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = cmake_system_processor
        if "arm" in self.settings.arch:
            self._cmake.definitions["CROSS_COMPILE_ARM"] = tools.cross_building(self.settings)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "source", "CMakeLists.txt")
        tools.replace_in_file(cmakelists,
                                "if((WIN32 AND ENABLE_CLI) OR (WIN32 AND ENABLE_SHARED))",
                                "if(FALSE)")
        if self.settings.os == "Android":
            tools.replace_in_file(cmakelists,
                "list(APPEND PLATFORM_LIBS pthread)", "")
            tools.replace_in_file(cmakelists,
                "list(APPEND PLATFORM_LIBS rt)", "")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        if self.options.shared:
            if self.settings.compiler == "Visual Studio":
                static_lib = "x265-static.lib"
            else:
                static_lib = "libx265.a"
            os.unlink(os.path.join(self.package_folder, "lib", static_lib))

        if self.settings.compiler == "Visual Studio":
            name = "libx265.lib" if self.options.shared else "x265-static.lib"
            shutil.move(os.path.join(self.package_folder, "lib", name),
                        os.path.join(self.package_folder, "lib", "x265.lib"))

        if self.settings.os != "Windows" or not self.options.shared:
            tools.rmdir(os.path.join(self.package_folder, "bin"))
        else:
            for file in os.listdir(os.path.join(self.package_folder, "bin")):
                if not file.endswith(".dll"):
                    os.unlink(os.path.join(self.package_folder, "bin", file))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "x265"
        self.cpp_info.libs = ["x265"]
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("X265_API_IMPORTS")
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread", "m"])
            if not self.options.shared:
                if self.settings.compiler != "Visual Studio":
                    self.cpp_info.sharedlinkflags = ["-Wl,-Bsymbolic,-znoexecstack"]
        elif self.settings.os == "Android":
            self.cpp_info.libs.extend(["dl", "m"])
        libcxx = tools.stdcpp_library(self)
        if libcxx:
            self.cpp_info.system_libs.append(libcxx)
