from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"


class LibeventConan(ConanFile):
    name = "libevent"
    description = "libevent - an event notification library"
    topics = ("event", "notification", "networking", "async")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libevent/libevent"
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "disable_threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "disable_threads": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_openssl:
            tc.variables["OPENSSL_ROOT_DIR"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        tc.cache_variables["EVENT__LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        tc.variables["EVENT__DISABLE_DEBUG_MODE"] = self.settings.build_type == "Release"
        tc.variables["EVENT__DISABLE_OPENSSL"] = not self.options.with_openssl
        tc.variables["EVENT__DISABLE_THREAD_SUPPORT"] = self.options.disable_threads
        tc.variables["EVENT__DISABLE_BENCHMARK"] = True
        tc.variables["EVENT__DISABLE_TESTS"] = True
        tc.variables["EVENT__DISABLE_REGRESS"] = True
        tc.variables["EVENT__DISABLE_SAMPLES"] = True
        # libevent uses static runtime (MT) for static builds by default
        if is_msvc(self):
            tc.variables["EVENT__MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # relocatable shared libs on macOS
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "AddEventLibrary.cmake"),
                              "INSTALL_NAME_DIR \"${CMAKE_INSTALL_PREFIX}/lib\"",
                              "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Libevent")
        self.cpp_info.set_property("pkg_config_name", "libevent") # exist in libevent for historical reason

        # core
        self.cpp_info.components["core"].set_property("cmake_target_name", "libevent::core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "libevent_core")
        self.cpp_info.components["core"].libs = ["event_core"]
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.disable_threads:
            self.cpp_info.components["core"].system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs = ["ws2_32", "advapi32", "iphlpapi"]

        # extra
        self.cpp_info.components["extra"].set_property("cmake_target_name", "libevent::extra")
        self.cpp_info.components["extra"].set_property("pkg_config_name", "libevent_extra")
        self.cpp_info.components["extra"].libs = ["event_extra"]
        if self.settings.os == "Windows":
            self.cpp_info.components["extra"].system_libs = ["shell32"]
        self.cpp_info.components["extra"].requires = ["core"]

        # openssl
        if self.options.with_openssl:
            self.cpp_info.components["openssl"].set_property("cmake_target_name", "libevent::openssl")
            self.cpp_info.components["openssl"].set_property("pkg_config_name", "libevent_openssl")
            self.cpp_info.components["openssl"].libs = ["event_openssl"]
            self.cpp_info.components["openssl"].requires = ["core", "openssl::openssl"]

        # pthreads
        if self.settings.os != "Windows" and not self.options.disable_threads:
            self.cpp_info.components["pthreads"].set_property("cmake_target_name", "libevent::pthreads")
            self.cpp_info.components["pthreads"].set_property("pkg_config_name", "libevent_pthreads")
            self.cpp_info.components["pthreads"].libs = ["event_pthreads"]
            self.cpp_info.components["pthreads"].requires = ["core"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Libevent"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Libevent"
