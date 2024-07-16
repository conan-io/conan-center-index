from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rename, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"


class Libx265Conan(ConanFile):
    name = "libx265"
    description = "x265 is the leading H.265 / HEVC encoder software library"
    topics = ("x265", "codec", "video", "H.265")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x265.html"
    license = ("GPL-2.0-only", "commercial")  # https://bitbucket.org/multicoreware/x265/src/default/COPYING

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "assembly": [True, False],
        "bit_depth": [8, 10, 12],
        "HDR10": [True, False],
        "SVG_HEVC_encoder": [True, False],
        "with_numa": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "assembly": True,
        "bit_depth": 8,
        "HDR10": False,
        "SVG_HEVC_encoder": False,
        "with_numa": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_numa
        # FIXME: Disable assembly by default if host is arm and compiler apple-clang for the moment.
        # Indeed, apple-clang is not able to understand some asm instructions of libx265
        # FIXME: Disable assembly by default if host is Android for the moment. It fails to build
        if (self.settings.compiler == "apple-clang" and "arm" in self.settings.arch) or self.settings.os == "Android":
            self.options.assembly = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_numa", False):
            self.requires("libnuma/2.0.14")

    def validate_build(self):
        if cross_building(self) and self.settings.os == "Android" and self.options.assembly:
            # FIXME: x265 uses custom command to invoke clang to compile assembly files.
            #   clang++ -fPIC -c src/source/common/aarch64/mc-a.S -o mc-a.S.o
            #   FAILED: mc-a.S.o libx2f309356bd8526/b/build/Release/mc-a.S.o
            #   clang++ -fPIC -c src/source/common/aarch64/mc-a.S -o mc-a.S.o
            #   <instantiation>:11:9: error: unknown directive
            #           .func x265_pixel_avg_pp_4x4_neon
            raise ConanInvalidConfiguration(f"{self.ref} fails to build with '&:assembly=True' for Android. Contributions are welcome.")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared not supported with static runtime")

        if self.settings.compiler == "apple-clang" and "arm" in self.settings.arch and self.options.assembly:
            # Undefined symbols for architecture arm64:
            # "x265::setupAssemblyPrimitives(x265::EncoderPrimitives&, int)", referenced from:
            # x265::x265_setup_primitives(x265_param*) in libx265.a[20](primitives.cpp.o)
            # ld: symbol(s) not found for architecture arm64
            raise ConanInvalidConfiguration(f"{self.ref} fails to build for Mac M1. Contributions are welcome.")

    def build_requirements(self):
        if self.options.assembly:
            if self.settings.arch in ["x86", "x86_64"]:
                self.tool_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_ASSEMBLY"] = self.options.assembly
        tc.variables["ENABLE_LIBNUMA"] = self.options.get_safe("with_numa", False)
        if self.settings.os == "Macos":
            tc.variables["CMAKE_SHARED_LINKER_FLAGS"] = "-Wl,-read_only_relocs,suppress"
        tc.variables["HIGH_BIT_DEPTH"] = self.options.bit_depth != 8
        tc.variables["MAIN12"] = self.options.bit_depth == 12
        tc.variables["ENABLE_HDR10_PLUS"] = self.options.HDR10
        tc.variables["ENABLE_SVT_HEVC"] = self.options.SVG_HEVC_encoder
        if is_msvc(self):
            tc.variables["STATIC_LINK_CRT"] = is_msvc_static_runtime(self)
        if self.settings.os == "Linux":
            tc.variables["PLATFORM_LIBS"] = "dl"
        if "arm" in self.settings.arch:
            tc.variables["CROSS_COMPILE_ARM"] = cross_building(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "source", "CMakeLists.txt")
        replace_in_file(self, cmakelists,
                                "if((WIN32 AND ENABLE_CLI) OR (WIN32 AND ENABLE_SHARED))",
                                "if(FALSE)")
        if self.settings.os == "Android":
            replace_in_file(self, cmakelists, "list(APPEND PLATFORM_LIBS pthread)", "")
            replace_in_file(self, cmakelists, "list(APPEND PLATFORM_LIBS rt)", "")
        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        replace_in_file(self, cmakelists,
                        "add_definitions(-ffast-math)",
                        "add_definitions(-ffast-math -fno-finite-math-only)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "source"))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        if self.options.shared:
            if is_msvc(self):
                static_lib = "x265-static.lib"
            else:
                static_lib = "libx265.a"
            os.unlink(os.path.join(self.package_folder, "lib", static_lib))

        if is_msvc(self):
            name = "libx265.lib" if self.options.shared else "x265-static.lib"
            rename(self, os.path.join(self.package_folder, "lib", name),
                         os.path.join(self.package_folder, "lib", "x265.lib"))

        if self.settings.os == "Windows" and self.options.shared:
            rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "x265")
        self.cpp_info.libs = ["x265"]
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("X265_API_IMPORTS")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "m", "rt"])
            if not self.options.shared:
                self.cpp_info.sharedlinkflags = ["-Wl,-Bsymbolic,-znoexecstack"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["dl", "m"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                if self.settings.os == "Android" and self.settings.compiler.libcxx == "c++_static":
                    self.cpp_info.system_libs.append("c++abi")
                self.cpp_info.system_libs.append(libcxx)
