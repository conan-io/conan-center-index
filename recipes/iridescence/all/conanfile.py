from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, rename
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class IridescenceConan(ConanFile):
    name = "iridescence"
    description = "3D visualization library for rapid prototyping of 3D algorithms"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://koide3.github.io/iridescence"
    topics = ("visualization", "imgui", "opengl", "localization", "mapping", "point-cloud", "slam")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "imgui_docking": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "imgui_docking": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("assimp/5.3.1")
        self.requires("boost/1.84.0", transitive_headers=True)
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("glm/cci.20230113")
        self.requires("libjpeg/9e")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("portable-file-dialogs/0.1.0", transitive_headers=True)
        docking = '-docking' if self.options.imgui_docking else ''
        # Would prefer imgui/1.89.9-docking and implot/0.16, but they would cause a version conflict on CCI
        self.requires(f"imgui/1.89.4{docking}", transitive_headers=True, transitive_libs=True)
        self.requires("imguizmo/1.83")
        self.requires("implot/0.14")
        self.requires("glfw/3.4", transitive_headers=True, transitive_libs=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libglvnd/1.7.0")
            self.requires("xorg/system")
        else:
            self.requires("opengl/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared builds are not supported on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMGUI_BACKENDS"] = os.path.join(self.dependencies["imgui"].package_folder, "res", "bindings").replace("\\", "/")
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["BUILD_PYTHON_BINDINGS"] = "OFF"
        tc.variables["BUILD_WITH_MARCH_NATIVE"] = "OFF"
        tc.variables["BUILD_EXT_TESTS"] = "OFF"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "iridescence")
        self.cpp_info.set_property("cmake_target_name", "iridescence::iridescence")
        self.cpp_info.set_property("pkg_config_name", "iridescence")

        self.cpp_info.libs = ["iridescence", "gl_imgui"]
        self.cpp_info.includedirs.append(os.path.join("include", "iridescence"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
