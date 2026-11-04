from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"

class GeometricToolsRecipe(ConanFile):
    name = "geometrictoolsengine"
    description = "Geometric Tools Engine"
    topics = ("gte", "geometry", "graphics", "mathematics", "header-only")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.geometrictools.com/"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    # Automatically manage the package ID clearing of settings and options
    implements = ["auto_header_only"]

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "GTE/Mathematics"),
            dst=os.path.join(self.package_folder, "include/Mathematics"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GeometricToolsEngine")
        # Using an explicit target name ('Mathematics') for future expansion to
        # multiple components ('MathematicsGPU', etc.)
        self.cpp_info.set_property("cmake_target_name", "GeometricToolsEngine::Mathematics")

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("GTE_USE_MSWINDOWS")
        else:
            self.cpp_info.defines.append("GTE_USE_LINUX")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
