from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, rename, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.9"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("assimp/5.4.2")
        self.requires("boost/1.84.0", transitive_headers=True)
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("glm/1.0.1")
        self.requires("libjpeg/9e")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("portable-file-dialogs/0.1.0", transitive_headers=True)
        # Upstream uses -docking version of imgui, but it would cause version conflicts on CCI
        self.requires("imgui/1.90.5", transitive_headers=True, transitive_libs=True)
        self.requires("imguizmo/cci.20231114")
        self.requires("implot/0.16")
        self.requires("glfw/3.4", transitive_headers=True, transitive_libs=True)
        self.requires("opengl/system")
        # https://github.com/koide3/iridescence/blob/7034275ee6516eb4d155f645cd8327173edfeb9d/thirdparty/gl3w/GL/glcorearb.h#L82
        self.requires("khrplatform/cci.20200529", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

        if is_msvc(self):
            # Build fails with several compilation errors
            raise ConanInvalidConfiguration("MSVC is not supported")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared builds are not supported on Windows")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        if Version(self.dependencies["imgui"].ref.version) >= "1.90":
            # https://github.com/ocornut/imgui/blob/master/imgui.cpp#L460
            replace_in_file(self, os.path.join(self.source_folder, "src", "guik", "viewer", "viewer_ui.cpp"),
                            "ImGui::GetWindowContentRegionWidth()",
                            "(ImGui::GetWindowContentRegionMax().x - ImGui::GetWindowContentRegionMin().x)")


    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMGUI_BACKENDS"] = os.path.join(self.dependencies["imgui"].package_folder, "res", "bindings").replace("\\", "/")
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["BUILD_PYTHON_BINDINGS"] = "OFF"
        tc.variables["BUILD_WITH_MARCH_NATIVE"] = "OFF"
        tc.variables["BUILD_EXT_TESTS"] = "OFF"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if "docking" not in str(self.dependencies["imgui"].ref.version):
            tc.preprocessor_definitions["ImGuiConfigFlags_DockingEnable"] = "0"
        if self.settings.os == "Windows":
            # TODO: submit a patch upstream
            tc.preprocessor_definitions["_USE_MATH_DEFINES"] = ""
            tc.preprocessor_definitions["NOMINMAX"] = ""
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        VirtualBuildEnv(self).generate()

    def build(self):
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
        self.cpp_info.set_property("cmake_file_name", "Iridescence")
        self.cpp_info.set_property("cmake_target_name", "Iridescence::Iridescence")

        self.cpp_info.libs = ["iridescence"]
        self.cpp_info.includedirs.append(os.path.join("include", "iridescence"))

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
