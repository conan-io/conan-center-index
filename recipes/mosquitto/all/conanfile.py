import os
from conans import CMake, ConanFile, tools

class MosquittoConan(ConanFile):
    name = "mosquitto"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse/mosquitto"
    topics = ("mqtt", "broker", "libwebsockets", "mosquitto", "eclipse-iot")
    license = "EPL-1.0"
    description = "Eclipse Mosquitto - An open source MQTT broker"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_tls": [True, False],
               "with_mosquittopp": [True, False],
               "with_srv": [True, False],
               "with_binaries": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_tls": True,
                       "with_mosquittopp": True,
                       "with_srv": True,
                       "with_binaries": True}
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_mosquittopp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_tls:
            self.requires.add("openssl/1.1.1g")
        if self.options.with_srv:
            self.requires.add("c-ares/1.16.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.replace("-", ".") + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["WITH_SRV"] = self.options.with_srv
            self._cmake.definitions["WITH_BINARIES"] = self.options.with_binaries
            self._cmake.definitions["WITH_MOSQUITTOPP"] = self.options.with_mosquittopp
            self._cmake.definitions["WITH_TLS"] = self.options.with_tls
            self._cmake.definitions["DOCUMENTATION"] = False
            self._cmake.definitions["CMAKE_INSTALL_SYSCONFDIR"] = "share"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="edl-v10", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="epl-v10", dst="licenses", src=self._source_subfolder)
        if self.options.with_binaries:
            self.copy(pattern="mosquitto.conf", src=self._source_subfolder, dst="bin")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(["rt", "pthread", "dl"])

        if self.options.with_binaries:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
