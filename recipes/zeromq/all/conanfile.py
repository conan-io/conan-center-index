from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class ZeroMQConan(ConanFile):
    name = "zeromq"
    homepage = "https://github.com/zeromq/libzmq"
    description = "ZeroMQ is a community of projects focused on decentralized messaging and computing"
    topics = ("zmq", "libzmq", "message-queue", "asynchronous")
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encryption": [None, "libsodium", "tweetnacl"],
        "with_norm": [True, False],
        "poller": [None, "kqueue", "epoll", "devpoll", "pollset", "poll", "select"],
        "with_draft_api": [True, False],
        "with_websocket": [True, False],
        "with_radix_tree": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encryption": "libsodium",
        "with_norm": False,
        "poller": None,
        "with_draft_api": False,
        "with_websocket": False,
        "with_radix_tree": False,
    }

    generators = "cmake", "cmake_find_package"
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

    def requirements(self):
        if self.options.encryption == "libsodium":
            self.requires("libsodium/1.0.18")
        if self.options.with_norm:
            self.requires("norm/1.5.9")

    def validate(self):
        if self.settings.os == "Windows" and self.options.with_norm:
            raise ConanInvalidConfiguration(
                "Norm and ZeroMQ are not compatible on Windows yet"
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_CURVE"] = bool(self.options.encryption)
        self._cmake.definitions["WITH_LIBSODIUM"] = self.options.encryption == "libsodium"
        self._cmake.definitions["ZMQ_BUILD_TESTS"] = False
        self._cmake.definitions["WITH_PERF_TOOL"] = False
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["ENABLE_CPACK"] = False
        self._cmake.definitions["WITH_DOCS"] = False
        self._cmake.definitions["WITH_DOC"] = False
        self._cmake.definitions["WITH_NORM"] = self.options.with_norm
        self._cmake.definitions["ENABLE_DRAFTS"] = self.options.with_draft_api
        self._cmake.definitions["ENABLE_WS"] = self.options.with_websocket
        self._cmake.definitions["ENABLE_RADIX_TREE"] = self.options.with_radix_tree
        if self.options.poller:
            self._cmake.definitions["POLLER"] = self.options.poller
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        os.unlink(os.path.join(self._source_subfolder, "builds", "cmake", "Modules", "FindSodium.cmake"))

        if self.options.encryption == "libsodium":
            os.rename("Findlibsodium.cmake", "FindSodium.cmake")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_FOUND",
                                       "libsodium_FOUND")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_INCLUDE_DIRS",
                                       "libsodium_INCLUDE_DIRS")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_LIBRARIES",
                                       "libsodium_LIBRARIES")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "CMake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._libzmq_target: "ZeroMQ::{}".format(self._libzmq_target)}
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
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _libzmq_target(self):
        return "libzmq" if self.options.shared else "libzmq-static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZeroMQ")
        self.cpp_info.set_property("cmake_target_name", self._libzmq_target)
        self.cpp_info.set_property("pkg_config_name", "libzmq")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libzmq"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["libzmq"].system_libs = ["iphlpapi", "ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libzmq"].system_libs = ["pthread", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.components["libzmq"].defines.append("ZMQ_STATIC")
        if self.options.with_draft_api:
            self.cpp_info.components["libzmq"].defines.append("ZMQ_BUILD_DRAFT_API")
        if self.options.with_websocket and self.settings.os != "Windows":
            self.cpp_info.components["libzmq"].system_libs.append("bsd")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "ZeroMQ"
        self.cpp_info.names["cmake_find_package_multi"] = "ZeroMQ"
        self.cpp_info.names["pkg_config"] = "libzmq"
        self.cpp_info.components["libzmq"].names["cmake_find_package"] = self._libzmq_target
        self.cpp_info.components["libzmq"].names["cmake_find_package_multi"] = self._libzmq_target
        self.cpp_info.components["libzmq"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libzmq"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["libzmq"].set_property("cmake_target_name", self._libzmq_target)
        if self.options.encryption == "libsodium":
            self.cpp_info.components["libzmq"].requires.append("libsodium::libsodium")
        if self.options.with_norm:
            self.cpp_info.components["libzmq"].requires.append("norm::norm")
