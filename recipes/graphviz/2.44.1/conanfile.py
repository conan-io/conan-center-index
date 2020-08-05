from conans import ConanFile, tools, CMake
import os

class Graphviz(ConanFile):
    name = "graphviz"
    description = "Conan installer for Graphviz"
    topics = ("conan", "graphviz", "dot", "doxygen", "installer")
    url = "https://gitlab.com/graphviz/graphviz/"
    homepage = "https://graphviz.org/"
    license = "Common Public License Version 1.0"
    generators = "virtualrunenv", "cmake"
    settings = "os", "arch", "compiler", "build_type"

    _cmake = None
    _source_subfolder = "source_subfolder"
    short_paths = True

    def build_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.5.3")
            self.build_requires("cairo/1.17.2@bincrafters/stable")

        if tools.os_info.is_windows and self.settings.os == "Windows":
            self.build_requires("msys2/20200517")
            self.build_requires("strawberryperl/5.30.0.1")
            self.build_requires("winflexbison/2.5.22")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "%s-%s" % (self.name, self.version)
        os.rename(folder_name, self._source_subfolder)
        # Get windows dependencies from official repo
        if tools.os_info.is_windows and self.settings.os == "Windows":
            git = tools.Git(folder=os.path.join(self._source_subfolder, "windows", "dependencies", "libraries"))
            git.clone("https://github.com/ErwinJanssen/graphviz-windows-dependencies.git", shallow=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(source_folder=self._source_subfolder)
            if tools.os_info.is_windows and self.settings.os == "Windows" and (self.settings.arch == "x86" or self.settings.arch == "x86_64"):
                arch = str(self.settings.arch).replace("86_", "")
                self._cmake.definitions["CMAKE_LIBRARY_PATH"]=os.path.join(self.build_folder, self._source_subfolder,
                    "windows", "dependencies", "libraries", arch, "lib")
        return self._cmake

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_apt:
                packages = ["libltdl-dev"]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["libtool-ltdl-devel"]
            elif tools.os_info.with_pacman:
                packages = ["libtool"]
            elif tools.os_info.with_zypper:
                packages = ["libltdl7"]
            else:
                self.output.warn("Do not know how to install 'libltdl' for {}.".format(tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        if tools.os_info.is_linux and self.settings.os == "Linux":
            os.environ['LD_LIBRARY_PATH'] = os.path.join(self.package_folder, "lib")
        # We need to configure dot before use
        self.run(os.path.join(self.package_folder, "bin", "dot -c"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if tools.os_info.is_linux and self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
