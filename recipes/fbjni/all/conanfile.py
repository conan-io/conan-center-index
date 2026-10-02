from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, save
import os
import textwrap


required_conan_version = ">=2.0.9"


class FbjniConan(ConanFile):
    name = "fbjni"
    description = "A library designed to simplify the usage of the Java Native Interface"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookincubator/fbjni"
    topics = ("jni", "java", "java-native-interface")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "system_java": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "system_java": False,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _jdk_reference(self):
        return "zulu-openjdk/21.0.11"

    @property
    def _cmake_module_path(self):
        return os.path.join("lib", "cmake", "conan-official-fbjni-jni.cmake")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        # Only selects where jni.h comes from; the binary is the same either way
        del self.info.options.system_java

    def validate(self):
        # Upstream does not build on Windows: win32/jni_md.h typedefs jint as long, see the
        # comment in upstream's CMakeLists.txt
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Windows; upstream's CMakeLists.txt explains why.")
        # Android builds take a different upstream path (NDK jni.h, liblog) that this recipe does not
        # exercise; upstream publishes a Prefab AAR (com.facebook.fbjni:fbjni) for Android
        if self.settings.os == "Android":
            raise ConanInvalidConfiguration(f"{self.ref} is not packaged for Android; use upstream's com.facebook.fbjni:fbjni AAR.")
        check_min_cppstd(self, 17)

    def validate_build(self):
        if self.options.system_java:
            self._system_java_home()

    def build_requirements(self):
        if not self.options.system_java:
            self.tool_requires(self._jdk_reference)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _system_java_home(self):
        java_home = self.conf.get("user.fbjni:java_home") or os.environ.get("JAVA_HOME")
        if not java_home:
            raise ConanInvalidConfiguration(
                f"{self.ref} with system_java=True needs a JDK: set conf user.fbjni:java_home or the JAVA_HOME environment variable.")
        if not os.path.isfile(os.path.join(java_home, "include", "jni.h")):
            raise ConanInvalidConfiguration(f"{self.ref}: no include/jni.h under JDK '{java_home}'.")
        return java_home

    def _java_home(self):
        if self.options.system_java:
            return self._system_java_home()
        return self.dependencies.build["zulu-openjdk"].package_folder

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["JAVA_HOME"] = self._java_home().replace("\\", "/")
        tc.cache_variables["FBJNI_SKIP_TESTS"] = True
        tc.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Let compiler.cppstd and build_type pick the standard and optimization level
        # https://github.com/facebookincubator/fbjni/issues/124
        replace_in_file(self, cmakelists, "  -std=c++20\n", "")
        replace_in_file(self, cmakelists, "  -O3\n  -DNDEBUG\n", "")
        # Honor the shared option: https://github.com/facebookincubator/fbjni/issues/124
        replace_in_file(self, cmakelists,
                        "add_library(fbjni SHARED ${fbjni_SOURCES})",
                        "add_library(fbjni ${fbjni_SOURCES})")
        # pthread_* and dladdr live in libpthread and libdl before glibc 2.34; without these the
        # shared library only resolves them inside a JVM, which has already loaded both
        # https://github.com/facebookincubator/fbjni/issues/123
        replace_in_file(self, cmakelists,
                        "target_compile_options(fbjni PRIVATE -DBUILDING_FBJNI)",
                        "target_compile_options(fbjni PRIVATE -DBUILDING_FBJNI)\n"
                        "find_package(Threads REQUIRED)\n"
                        "target_link_libraries(fbjni PRIVATE Threads::Threads ${CMAKE_DL_LIBS})")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Upstream installs no headers; ship the same cxx/ tree as its Android Prefab package
        for subdir in ("fbjni", "lyra"):
            copy(self, "*.h", os.path.join(self.source_folder, "cxx", subdir),
                 os.path.join(self.package_folder, "include", subdir))
        rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_module()

    def _create_cmake_module(self):
        # fbjni's headers include <jni.h>; consumers take it from their own JDK. OPTIONAL_COMPONENTS
        # keeps CMake >= 3.24 from requiring AWT and libjvm, which a JNI library must not link.
        content = textwrap.dedent("""\
            find_package(JNI REQUIRED OPTIONAL_COMPONENTS JVM)
            set_property(TARGET fbjni::fbjni APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${JNI_INCLUDE_DIRS})
        """)
        save(self, os.path.join(self.package_folder, self._cmake_module_path), content)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fbjni")
        self.cpp_info.set_property("cmake_target_name", "fbjni::fbjni")
        self.cpp_info.set_property("cmake_build_modules", [self._cmake_module_path])
        self.cpp_info.libs = ["fbjni"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl", "m"])
