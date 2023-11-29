import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get

required_conan_version = ">=1.53.0"


class DjinniSupportLib(ConanFile):
    name = "djinni-support-lib"
    description = "Djinni is a tool for generating cross-language type declarations and interface bindings"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://djinni.xlcpp.dev"
    topics = ("java", "Objective-C", "Android", "iOS")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "target": ["jni", "objc", "auto"],
        "system_java": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "target": "auto",
        "system_java": False,
    }

    @property
    def _objc_support(self):
        return self.options.target == "objc"

    @property
    def _jni_support(self):
        return self.options.target == "jni"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # Set default target based on OS
        self.options.target = "objc" if is_apple_os(self) else "jni"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if not self.options.system_java and self._jni_support:
            self.tool_requires("zulu-openjdk/21.0.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if not self.options.shared:
            tc.variables["DJINNI_STATIC_LIB"] = True
        tc.variables["DJINNI_WITH_OBJC"] = self._objc_support
        tc.variables["DJINNI_WITH_JNI"] = self._jni_support
        if self._jni_support:
            tc.variables["JAVA_AWT_LIBRARY"] = "NotNeeded"
            tc.variables["JAVA_AWT_INCLUDE_PATH"] = self.source_folder.replace("\\", "/")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        # these should not be here, but to support old generated files ....
        if self._objc_support:
            self.cpp_info.includedirs.append(os.path.join("include", "djinni", "objc"))
        if self._jni_support:
            self.cpp_info.includedirs.append(os.path.join("include", "djinni", "jni"))

        if self._objc_support:
            self.cpp_info.frameworks = ["Foundation", "CoreFoundation"]
