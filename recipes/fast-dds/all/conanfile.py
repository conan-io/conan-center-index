from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class FastDDSConan(ConanFile):
    name = "fast-dds"
    license = "Apache-2.0"
    homepage = "https://fast-dds.docs.eprosima.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The most complete OSS DDS implementation for embedded systems."
    topics = ("dds", "middleware", "ipc")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "5",
            "clang": "3.9",
            "apple-clang": "8",
        }

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
        self.requires("tinyxml2/9.0.0")
        self.requires("asio/1.21.0")
        self.requires("fast-cdr/1.0.23")
        self.requires("foonathan-memory/0.7.1")
        self.requires("boost/1.75.0")  # boost/1.76 is required by version 2.3.2, boost/1.75.0 required for 2.3.3 by Windows
        if self.options.with_ssl:
            self.requires("openssl/1.1.1m")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and tools.scm.Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                "{} requires C++{} support. {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard,
                    self.settings.compiler, self.settings.compiler.version
                )
            )
        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            # This combination leads to an fast-dds error when linking
            # linking dynamic '*.dll' and static MT runtime
            raise ConanInvalidConfiguration("Mixing a dll {} library with a static runtime is a bad idea".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_MEMORY_TOOLS"] = False
        self._cmake.definitions["NO_TLS"] = not self.options.with_ssl
        self._cmake.definitions["SECURITY"] = self.options.with_ssl
        self._cmake.definitions["EPROSIMA_INSTALLER_MINION"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.files.rename(self, 
            src=os.path.join(self.package_folder, "tools"),
            dst=os.path.join(os.path.join(self.package_folder, "bin", "tools"))
        )
        tools.files.rm(self, 
            directory=os.path.join(self.package_folder, "lib"),
            pattern="*.pdb"
        )
        tools.files.rm(self, 
            directory=os.path.join(self.package_folder, "bin"),
            pattern="*.pdb"
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fastrtps": "fastdds::fastrtps"}
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fastdds")

        # component fastrtps
        self.cpp_info.components["fastrtps"].set_property("cmake_target_name", "fastrtps")
        self.cpp_info.components["fastrtps"].libs = tools.files.collect_libs(self, self)
        self.cpp_info.components["fastrtps"].requires = [
            "fast-cdr::fast-cdr",
            "asio::asio",
            "tinyxml2::tinyxml2",
            "foonathan-memory::foonathan-memory",
            "boost::boost"
        ]
        if self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
            self.cpp_info.components["fastrtps"].system_libs.append("pthread")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["fastrtps"].system_libs.extend(["rt", "dl", "atomic"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["fastrtps"].system_libs.extend(["iphlpapi","shlwapi"])
            if self.options.shared:
                self.cpp_info.components["fastrtps"].defines.append("FASTRTPS_DYN_LINK")
        if self.options.with_ssl:
            self.cpp_info.components["fastrtps"].requires.append("openssl::openssl")

        # component fast-discovery
        # FIXME: actually conan generators don't know how to create an executable imported target
        self.cpp_info.components["fast-discovery-server"].set_property("cmake_target_name", "fastdds::fast-discovery-server")
        self.cpp_info.components["fast-discovery-server"].bindirs = ["bin"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var for fast-dds::fast-discovery-server with: {}".format(bin_path)),
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "fastdds"
        self.cpp_info.names["cmake_find_package_multi"] = "fastdds"
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_package"] = "fast-discovery-server"
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_package_multi"] = "fast-discovery-server"
