import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime

required_conan_version = ">=1.53.0"


class NvclothConan(ConanFile):
    name = "nvcloth"
    description = "NvCloth is a library that provides low level access to a cloth solver designed for realtime interactive applications."
    license = "Nvidia Source Code License (1-Way Commercial)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIAGameWorks/NvCloth"
    topics = ("physics", "physics-engine", "physics-simulation", "game-development", "cuda")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_cuda": [True, False],
        "use_dx11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_cuda": False,
        "use_dx11": False,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "FreeBSD", "Macos", "Android", "iOS"]:
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported")

        if self.settings.os in ["Windows", "Macos"] and not self.options.shared:
            raise ConanInvalidConfiguration(f"Static builds are not supported on {self.settings.os}")
        if self.settings.os in ["iOS", "Android"] and self.options.shared:
            raise ConanInvalidConfiguration(f"Shared builds are not supported on {self.settings.os}")

        if self.settings.build_type not in ["Debug", "RelWithDebInfo", "Release"]:
            raise ConanInvalidConfiguration(f"{self.settings.build_type} build_type is not supported")

        check_min_vs(self, 150)
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _target_build_platform(self):
        return {
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "mac",
            "Android": "android",
            "iOS": "ios",
        }.get(str(self.settings.os))

    def generate(self):
        tc = CMakeToolchain(self)
        if not self.options.shared:
            tc.variables["PX_STATIC_LIBRARIES"] = 1
        tc.variables["STATIC_WINCRT"] = is_msvc_static_runtime(self)
        tc.variables["NV_CLOTH_ENABLE_CUDA"] = self.options.use_cuda
        tc.variables["NV_CLOTH_ENABLE_DX11"] = self.options.use_dx11
        tc.variables["TARGET_BUILD_PLATFORM"] = self._target_build_platform
        tc.generate()

        env = Environment()
        env.define_path("GW_DEPS_ROOT", self.source_folder)
        env.vars(self).save_script("conan_build_vars")

    def _remove_samples(self):
        rmdir(self, os.path.join(self.source_folder, "NvCloth", "samples"))

    def _patch_sources(self):
        # There is no reason to force consumer of PhysX public headers to use one of
        # NDEBUG or _DEBUG, since none of them relies on NDEBUG or _DEBUG
        replace_in_file(self, os.path.join(self.source_folder, "PxShared", "include", "foundation", "PxPreprocessor.h"),
                        "#error Exactly one of NDEBUG and _DEBUG needs to be defined!",
                        "// #error Exactly one of NDEBUG and _DEBUG needs to be defined!")
        shutil.copy(os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h"),
                    os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h.origin"))
        apply_conandata_patches(self)

        if self.settings.build_type == "Debug":
            shutil.copy(os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h"),
                        os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h.patched"))
            shutil.copy(os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h.origin"),
                        os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h"))

    def build(self):
        self._patch_sources()
        self._remove_samples()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        if self.settings.build_type == "Debug":
            shutil.copy(os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h.patched"),
                        os.path.join(self.source_folder, "NvCloth", "include", "NvCloth", "Callbacks.h"))
        copy(self, "NvCloth/license.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder, keep_path=False)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "NvCloth", "include"))
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "NvCloth", "extensions", "include"))
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "PxShared", "include"))
        copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dylib*", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
        copy(self, "*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nvcloth")
        self.cpp_info.set_property("cmake_target_name", "nvcloth::nvcloth")

        if self.settings.build_type == "Debug":
            debug_suffix = "DEBUG"
        else:
            debug_suffix = ""

        if self.settings.os == "Windows" and self.settings.arch == "x86_64":
            arch_suffix = "_x64"
        else:
            arch_suffix = ""

        self.cpp_info.libs = [f"NvCloth{debug_suffix}{arch_suffix}"]

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
