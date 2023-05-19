from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


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
        "encryption": [False, "libsodium", "tweetnacl"],
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

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
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_CURVE"] = bool(self.options.encryption)
        tc.variables["WITH_LIBSODIUM"] = self.options.encryption == "libsodium"
        tc.variables["ZMQ_BUILD_TESTS"] = False
        tc.variables["WITH_PERF_TOOL"] = False
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_TESTS"] = False
        tc.variables["ENABLE_CPACK"] = False
        tc.variables["WITH_DOCS"] = False
        tc.variables["WITH_DOC"] = False
        tc.variables["WITH_NORM"] = self.options.with_norm
        tc.variables["ENABLE_DRAFTS"] = self.options.with_draft_api
        tc.variables["ENABLE_WS"] = self.options.with_websocket
        tc.variables["ENABLE_RADIX_TREE"] = self.options.with_radix_tree
        if self.options.poller:
            tc.variables["POLLER"] = self.options.poller
        if is_msvc(self):
            tc.preprocessor_definitions["_NOEXCEPT"] = "noexcept"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.options.encryption == "libsodium":
            cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
            cpp_info_sodium = self.dependencies["libsodium"].cpp_info
            sodium_config = cpp_info_sodium.get_property("cmake_file_name") or "libsodium"
            sodium_target = cpp_info_sodium.get_property("cmake_target_name") or "libsodium::libsodium"
            find_sodium = "find_package(Sodium)" if Version(self.version) < "4.3.3" else "find_package(\"Sodium\")"
            replace_in_file(self, cmakelists, find_sodium, f"find_package({sodium_config} REQUIRED CONFIG)")
            replace_in_file(self, cmakelists, "SODIUM_FOUND", f"{sodium_config}_FOUND")
            replace_in_file(self, cmakelists, "SODIUM_INCLUDE_DIRS", f"{sodium_config}_INCLUDE_DIRS")
            replace_in_file(self, cmakelists, "${SODIUM_LIBRARIES}", sodium_target)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._libzmq_target: f"ZeroMQ::{self._libzmq_target}"},
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _libzmq_target(self):
        return "libzmq" if self.options.shared else "libzmq-static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZeroMQ")
        self.cpp_info.set_property("cmake_target_name", self._libzmq_target)
        self.cpp_info.set_property("pkg_config_name", "libzmq")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libzmq"].libs = collect_libs(self)
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
