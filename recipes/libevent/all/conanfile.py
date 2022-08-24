from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conan import ConanFile, tools
from conans import CMake
import os
import functools

required_conan_version = ">=1.45.0"


class LibeventConan(ConanFile):
    name = "libevent"
    description = "libevent - an event notification library"
    topics = ("event", "notification", "networking", "async")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libevent/libevent"
    license = "BSD-3-Clause"

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

    generators = "cmake", "cmake_find_package"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # relocatable shared libs on macOS
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "AddEventLibrary.cmake"),
                              "INSTALL_NAME_DIR \"${CMAKE_INSTALL_PREFIX}/lib\"",
                              "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if self.options.with_openssl:
            cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        cmake.definitions["EVENT__LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        cmake.definitions["EVENT__DISABLE_DEBUG_MODE"] = self.settings.build_type == "Release"
        cmake.definitions["EVENT__DISABLE_OPENSSL"] = not self.options.with_openssl
        cmake.definitions["EVENT__DISABLE_THREAD_SUPPORT"] = self.options.disable_threads
        cmake.definitions["EVENT__DISABLE_BENCHMARK"] = True
        cmake.definitions["EVENT__DISABLE_TESTS"] = True
        cmake.definitions["EVENT__DISABLE_REGRESS"] = True
        cmake.definitions["EVENT__DISABLE_SAMPLES"] = True
        # libevent uses static runtime (MT) for static builds by default
        if is_msvc(self):
            cmake.definitions["EVENT__MSVC_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
        
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))

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
