from conans import ConanFile, CMake, tools
import os
from conans.errors import ConanInvalidConfiguration
import textwrap

class FastDDSConan(ConanFile):

    name = "fast-dds"
    license = "Apache-2.0"
    homepage = "https://fast-dds.docs.eprosima.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The most complete OSS DDS implementation for embedded systems."
    topics = ("DDS", "Middleware", "IPC")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":           [True, False],
        "fPIC":             [True, False],
        "with_ssl":         [True, False]
    }
    default_options = {
        "shared":           False,
        "fPIC":             True,
        "with_ssl":         False
    }
    generators = "cmake", "cmake_find_package"
    _cmake = None
    exports_sources = ["patches/**", "CMakeLists.txt"]

    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _pkg_tools(self):
        return os.path.join(
            self.package_folder,
            "tools"
        )

    @property
    def _pkg_bin(self):
        return os.path.join(
            self.package_folder,
            "bin"
        )

    @property
    def _module_subfolder(self):
        return os.path.join(
            "lib",
            "cmake"
        )

    @property
    def _module_file_rel_path(self):
        return os.path.join(
            self._module_subfolder,
            "conan-target-properties.cmake"
        )
    
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
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)         
            self._cmake.definitions["BUILD_MEMORY_TOOLS"] = False
            self._cmake.definitions["NO_TLS"] = not self.options.with_ssl
            self._cmake.definitions["SECURITY"] = self.options.with_ssl
            self._cmake.definitions["EPROSIMA_INSTALLER_MINION"] = False
            self._cmake.configure()
        return self._cmake

    def requirements(self):
        self.requires("tinyxml2/7.1.0")
        self.requires("asio/1.18.2")
        self.requires("fast-cdr/1.0.21")
        self.requires("foonathan-memory/0.7.0")
        self.requires("boost/1.73.0")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1k")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if self.settings.os == "Windows":
            if ("MT" in self.settings.compiler.runtime and self.options.shared):
                # This combination leads to an fast-dds error when linking
                # linking dynamic '*.dll' and static MT runtime
                raise ConanInvalidConfiguration("Mixing a dll {} library with a static runtime is a bad idea".format(self.name))


    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(self._pkg_share)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rename(
            src=self._pkg_tools,
            dst=os.path.join(self._pkg_bin, "tools")
        )
        tools.remove_files_by_mask(
            directory=os.path.join(self.package_folder, "lib"),
            pattern="*.pdb"
        )
        tools.remove_files_by_mask(
            directory=os.path.join(self.package_folder, "bin"),
            pattern="*.pdb"
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fastrtps": "fastdds::fastrtps"}
        )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "fastdds"
        self.cpp_info.names["cmake_find_multi_package"] = "fastdds"
        # component fastrtps
        self.cpp_info.components["fastrtps"].names["cmake_find_package"]  = "fastrtps"
        self.cpp_info.components["fastrtps"].names["cmake_find_multi_package"] = "fastrtps"
        self.cpp_info.components["fastrtps"].libs = tools.collect_libs(self)
        self.cpp_info.components["fastrtps"].requires = [
            "fast-cdr::fast-cdr",
            "asio::asio",
            "tinyxml2::tinyxml2",
            "foonathan-memory::foonathan-memory",
            "boost::boost"
        ]
        if self.settings.os in ["Linux", "Macos", "Neutrino"]:
            self.cpp_info.components["fastrtps"].system_libs.append("pthread")
        if self.settings.os == "Linux":
            self.cpp_info.components["fastrtps"].system_libs.extend(["rt", "dl", "atomic"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["fastrtps"].system_libs.extend(["iphlpapi","shlwapi"])
            if self.options.shared:
                self.cpp_info.components["fastrtps"].defines.append("FASTRTPS_DYN_LINK")
        if self.options.with_ssl:
            self.cpp_info.components["fastrtps"].requires.append("openssl::openssl")
        self.cpp_info.components["fastrtps"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        # component fast-discovery
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_package"] = "fast-discovery-server"
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_multi_package"] = "fast-discovery-server"
        self.cpp_info.components["fast-discovery-server"].bindirs = ["bin"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var for fast-dds::fast-discovery-server with : {}".format(bin_path)),
        self.env_info.PATH.append(bin_path)
        # component tools
        self.cpp_info.components["tools"].names["cmake_find_package"] = "tools"
        self.cpp_info.components["tools"].names["cmake_find_multi_package"] = "tools"
        self.cpp_info.components["tools"].bindirs = [os.path.join("bin","tools")]
        bin_path = os.path.join(self._pkg_bin, "tools")
        self.output.info("Appending PATH env var for fast-dds::tools with : {}".format(bin_path)),
        self.env_info.PATH.append(bin_path)
