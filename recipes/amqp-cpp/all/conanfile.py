from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class AmqpcppConan(ConanFile):
    name = "amqp-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CopernicaMarketingSoftware/AMQP-CPP"
    topics = ("amqp", "network", "queue", "conan")
    license = "Apache-2.0"
    description = "C++ library for asynchronous non-blocking communication with RabbitMQ"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "linux_tcp_module": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "linux_tcp_module": True,
    }
    generators = "cmake"

    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.linux_tcp_module

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.get_safe("linux_tcp_module"):
            self.requires("openssl/1.1.1j")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("AMQP-CPP-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["AMQP-CPP_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["AMQP-CPP_BUILD_EXAMPLES"] = False
        self._cmake.definitions["AMQP-CPP_LINUX_TCP"] = self.options.get_safe("linux_tcp_module") or False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.install()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"amqpcpp": "amqpcpp::amqpcpp"}
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "amqpcpp"
        self.cpp_info.names["cmake_find_package"] = "amqpcpp"
        self.cpp_info.names["cmake_find_package_multi"] = "amqpcpp"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.libs = ["amqpcpp"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
