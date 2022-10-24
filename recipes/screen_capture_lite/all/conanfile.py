from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"

class ScreenCaptureLiteConan(ConanFile):
    name = "screen_capture_lite"
    license = "MIT"
    description = "cross platform screen/window capturing library "
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/smasherprog/screen_capture_lite"
    topics = ("screen-capture", "screen-ercorder")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "10",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support."
                )

        if self.info.settings.compiler == "clang" and self.info.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} does not support clang with libstdc++")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLE"] = False
        if is_msvc(self):
            # fix "error C2039: 'CheckForDuplicateEntries': is not a member of 'Microsoft::WRL::Details'"
            tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0.18362.0"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["screen_capture_lite_shared" if self.options.shared else "screen_capture_lite_static"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.requires.extend([
                "xorg::x11",
                "xorg::xinerama",
                "xorg::xext",
                "xorg::xfixes",
            ])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "dwmapi",
                "d3d11",
                "dxgi",
            ])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend([
                "AppKit",
                "AVFoundation",
                "Carbon",
                "Cocoa",
                "CoreFoundation",
                "CoreGraphics",
                "CoreMedia",
                "CoreVideo",
                "Foundation",
                "ImageIO",
            ])
