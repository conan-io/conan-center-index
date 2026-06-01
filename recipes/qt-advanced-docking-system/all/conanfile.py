import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class QtADS(ConanFile):
    name = "qt-advanced-docking-system"
    description = (
        "Qt Advanced Docking System lets you create customizable layouts "
        "using a full featured window docking system similar to what is found "
        "in many popular integrated development environments (IDEs) such as "
        "Visual Studio."
    )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System"
    topics = ("qt", "gui")

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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=5.15 <7]", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("qt/<host_version>")
        self.tool_requires("cmake/[>=3.27]") # to be able to use CMAKE_AUTOMOC_EXECUTABLE

    def validate(self):
        if Version(self.dependencies["qt"].ref.version) >= "6.0.0":
            check_min_cppstd(self, 17) # Qt6 requires C++17 as a minimum

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ADS_VERSION"] = self.version
        tc.cache_variables["BUILD_EXAMPLES"] = "OFF"
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        # The upstream CMakeLists.txt only sets CMAKE_MODULE_PATH inside an
        # if(NOT ADS_VERSION) block. Since we supply ADS_VERSION, that block is
        # skipped and src/CMakeLists.txt cannot find Versioning.cmake.
        tc.cache_variables["CMAKE_MODULE_PATH"] = os.path.join(self.source_folder, "cmake", "modules").replace("\\", "/")

        qt_tools_rootdir = self.conf.get("user.qt:tools_directory", None)
        if qt_tools_rootdir:
            tc.cache_variables["CMAKE_AUTOMOC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "moc.exe" if self.settings_build.os == "Windows" else "moc")
            tc.cache_variables["CMAKE_AUTORCC_EXECUTABLE"] = os.path.join(qt_tools_rootdir, "rcc.exe" if self.settings_build.os == "Windows" else "rcc")

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "gnu-lgpl-v2.1.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "license"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # Detect Qt major version from installed include directory name
        qt_major = 6 if Version(self.dependencies["qt"].ref.version) >= "6.0.0" else 5

        base_name = f"qtadvanceddocking-qt{qt_major}"
        self.cpp_info.includedirs.append(os.path.join("include", base_name))
        cmake_name = f"qt{qt_major}advanceddocking"
        lib_name = f"{base_name}d" if self.settings.build_type == "Debug" else base_name

        self.cpp_info.set_property("cmake_file_name", cmake_name)
        self.cpp_info.set_property("cmake_target_name", f"ads::{cmake_name}")

        if self.options.shared:
            self.cpp_info.libs = [lib_name]
        else:
            self.cpp_info.defines.append("ADS_STATIC")
            self.cpp_info.libs = [f"{lib_name}_static"]
