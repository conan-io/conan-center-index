from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class CzmqConan(ConanFile):
    name = "czmq"
    homepage = "https://github.com/zeromq/czmq"
    description = "High-level C binding for ZeroMQ"
    topics = ("zmq", "libzmq", "message-queue", "asynchronous")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_lz4": [True, False],
        "with_libuuid": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": True,
        "with_lz4": True,
        "with_libuuid": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # libuuid is not available on Windows
            del self.options.with_libuuid

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openssl/1.1.1m")  # zdigest depends on openssl
        self.requires("zeromq/4.3.4")
        if self.options.with_libcurl:
            self.requires("libcurl/7.80.0")
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.get_safe("with_libuuid"):
            self.requires("libuuid/1.0.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CZMQ_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CZMQ_BUILD_STATIC"] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "CMake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._czmq_target: "czmq::czmq"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _czmq_target(self):
        return "czmq" if self.options.shared else "czmq-static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "czmq")
        self.cpp_info.set_property("cmake_target_name", self._czmq_target)
        self.cpp_info.set_property("pkg_config_name", "libczmq")
        prefix = "lib" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.libs = ["{}czmq".format(prefix)]
        if not self.options.shared:
            self.cpp_info.defines.append("CZMQ_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("rpcrt4")
        if not self.options.shared:
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "libczmq"
