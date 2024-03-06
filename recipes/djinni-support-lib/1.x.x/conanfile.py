import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

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
        "with_jni": [True, False, "auto"],
        "with_objc": [True, False, "auto"],
        "with_python": [True, False, "auto"],
        "with_cppcli": [True, False, "auto"],
        "system_java": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jni": "auto",
        "with_objc": "auto",
        "with_python": "auto",
        "with_cppcli": "auto",
        "system_java": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        elif self.settings.os == "Android":
            self.options.system_java = True

    @property
    def _objc_support(self):
        if self.options.with_objc == "auto":
            return is_apple_os(self)
        else:
            return self.options.with_objc

    @property
    def _jni_support(self):
        if self.options.with_jni == "auto":
            return self.settings.os == "Android"
        else:
            return self.options.with_jni

    @property
    def _python_support(self):
        return self.options.with_python

    @property
    def _cppcli_support(self):
        if self.options.with_cppcli == "auto":
            return self.settings.os == "Windows"
        else:
            return self.options.with_cppcli

    @property
    def _supported_compilers(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def configure(self):
        if is_msvc(self) or self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if not (self._objc_support or self._jni_support or self._python_support or self._cppcli_support):
            raise ConanInvalidConfiguration(
                "Target language could not be determined automatically. Set at least one of 'with_jni',"
                " 'with_objc', 'with_python' or 'with_cppcli' options to `True`."
            )
        if self._cppcli_support:
            if self.settings.os != "Windows":
                raise ConanInvalidConfiguration(
                    "C++/CLI has been enabled on a non-Windows operating system. This is not supported."
                )
            if self._objc_support or self._jni_support or self._python_support:
                raise ConanInvalidConfiguration(
                    "C++/CLI is not yet supported with other languages enabled as well. "
                    "Disable 'with_jni', 'with_objc' and 'with_python' options for a valid configuration."
                )
            if self.options.shared:
                raise ConanInvalidConfiguration("C++/CLI does not support building as shared library")
            if is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration("'/clr' and '/MT' command-line options are incompatible")
        if self._python_support:
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration(
                    "Python on Windows is not fully yet supported, please see"
                    " https://github.com/cross-language-cpp/djinni-support-lib/issues."
                )
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._supported_compilers[str(self.settings.compiler)]
            if Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration(
                    "This package requires c++17 support. The current compiler does not support it."
                )
        except KeyError:
            self.output.warning(
                "This recipe has no support for the current compiler. Please consider adding it."
            )

    def build_requirements(self):
        if not self.options.system_java and self._jni_support:
            self.build_requires("zulu-openjdk/11.0.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.variables["DJINNI_WITH_OBJC"] = self._objc_support
        tc.variables["DJINNI_WITH_JNI"] = self._jni_support
        tc.variables["DJINNI_WITH_PYTHON"] = self._python_support
        tc.variables["DJINNI_WITH_CPPCLI"] = self._cppcli_support
        tc.variables["BUILD_TESTING"] = False
        if self._jni_support:
            tc.variables["JAVA_AWT_LIBRARY"] = "NotNeeded"
            tc.variables["JAVA_AWT_INCLUDE_PATH"] = "NotNeeded"
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
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
