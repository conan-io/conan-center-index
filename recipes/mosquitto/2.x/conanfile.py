import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class Mosquitto(ConanFile):
    name = "mosquitto"
    license = "EPL-2.0", "EPL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mosquitto.org"
    description = """Eclipse Mosquitto MQTT library, broker and more"""
    topics = ("MQTT", "IoT", "eclipse")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
                "with_tls": [True, False],
                "clients": [True, False],
                "broker": [True, False],
                "apps": [True, False],
                "plugins": [True, False],
                "with_cjson": [True, False],
            }
    default_options = {"shared": False,
                        "with_tls": True,
                        "clients": False,
                        "broker": False,
                        "apps": False,
                        "plugins": False,  # TODO, there is some logic, just enabling plugin does not work, needs also something else
                        "with_cjson": False ,
    }

    _cmake = None


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/1.1.1i")
        if self.options.with_cjson:
            self.requires("cjson/1.7.14")

    def configure(self):
        if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for any MT runtime is not supported")
        if self.options.with_cjson: # see _configure_cmake for the reason
            raise ConanInvalidConfiguration("Option with_cjson not yet supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_THREADING"] = self.settings.os != "Windows"
        self._cmake.definitions["WITH_PIC"] = self.settings.os != "Windows"
        self._cmake.definitions["WITH_STATIC_LIBRARIES"] = not self.options.shared
        self._cmake.definitions["WITH_TLS"] = self.options.with_tls
        self._cmake.definitions["WITH_CLIENTS"] = self.options.clients
        self._cmake.definitions["WITH_BROKER"] = self.options.broker
        self._cmake.definitions["WITH_APPS"] = self.options.apps
        self._cmake.definitions["WITH_PLUGINS"] = self.options.plugins
        self._cmake.definitions["DOCUMENTATION"] = False
        if self.options.with_tls:
            self._cmake.definitions["OPENSSL_SEARCH_PATH"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
            self._cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")

        # this does not work, and I do not know how to make cmake of mosquitto FIND_PACKAGE(cJSON) succeed
        # if self.options.with_cjson:
        #     self._cmake.definitions["cJSON_SEARCH_PATH"] = self.deps_cpp_info["cjson"].rootpath.replace("\\", "/")
        #     self._cmake.definitions["cJSON_ROOT_DIR"] = self.deps_cpp_info["cjson"].rootpath.replace("\\", "/")

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def _patch(self):
        if self.settings.os == "Windows":
            if self.options.with_tls:
                tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} crypt32")
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} crypt32")
                # This is so inconsequent, there is ws2_32 meanwhile in the build, but forgotten here
                tools.replace_in_file(os.path.join(self._source_subfolder, "apps", "mosquitto_passwd" ,"CMakeLists.txt"),
                                    "${OPENSSL_LIBRARIES}",
                                    "${OPENSSL_LIBRARIES} ws2_32 crypt32")
            tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"),
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS libmosquitto RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")
            tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "cpp", "CMakeLists.txt"),
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")",
                                "install(TARGETS mosquittopp RUNTIME DESTINATION \"${CMAKE_INSTALL_BINDIR}\" LIBRARY DESTINATION \"${CMAKE_INSTALL_LIBDIR}\" ARCHIVE DESTINATION \"${CMAKE_INSTALL_LIBDIR}\")")


    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("edl-v10", src=self._source_subfolder, dst="licenses")
        self.copy("edl-v20", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib","pkgconfig"))
        if not self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dll*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib*")

    def package_info(self):
        lib_suffix = "_static" if not self.options.shared else ""
        # FIXME: there should be no namespace for CMake targets
        self.cpp_info.components["libmosquitto"].name = "mosquitto"
        self.cpp_info.components["libmosquitto"].libs = ["mosquitto" + lib_suffix]
        self.cpp_info.components["libmosquitto"].names["pkgconfig"] = "libmosquitto"
        if self.options.with_tls:
            self.cpp_info.components["libmosquitto"].requires.append("openssl::openssl")
            self.cpp_info.components["libmosquitto"].defines.append("WITH_TLS")
        if self.settings.os == "Windows":
            self.cpp_info.components["libmosquitto"].system_libs.append("ws2_32")
            if self.options.with_tls:
                self.cpp_info.components["libmosquitto"].system_libs.append("crypt32")
        elif self.settings.os == "Linux":
            self.cpp_info.components["libmosquitto"].system_libs.extend(["rt", "pthread", "dl"])

        self.cpp_info.components["libmosquittopp"].name = "mosquittopp"
        self.cpp_info.components["libmosquittopp"].libs = ["mosquittopp" + lib_suffix]
        self.cpp_info.components["libmosquittopp"].requires = ["libmosquitto"]
        self.cpp_info.components["libmosquittopp"].names["pkgconfig"] = "libmosquittopp"
        if not self.options.shared:
            self.cpp_info.components["libmosquitto"].defines.append("LIBMOSQUITTO_STATIC")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
