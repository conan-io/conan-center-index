from conans import ConanFile, tools
import os


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://boostorg.github.io/build/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("conan", "installer", "boost", "builder")
    license = "BSL-1.0"
    settings = "os_build", "arch_build"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "build-" + \
            os.path.basename(self.conan_data["sources"][self.version]['url']).replace(
                ".tar.gz", "")
        os.rename(extracted_dir, "source")

    def build(self):
        use_windows_commands = os.name == 'nt'
        command = "build" if use_windows_commands else "./build.sh"
        build_dir = os.path.join(self.source_folder, "source")
        engine_dir = os.path.join(build_dir, "src", "engine")
        os.chdir(engine_dir)
        with tools.environment_append({"VSCMD_START_DIR": os.curdir}):
            if tools.get_env("CXXFLAGS") is not None:
                # Tell the b2 build to use the environment variable CXX for the compiler to use
                command += ' cxx'
            self.run(command)
        os.chdir(build_dir)
        command = os.path.join(
            engine_dir, "b2.exe" if use_windows_commands else "b2")
        full_command = \
            "{0} --ignore-site-config --prefix=../output --abbreviate-paths install".format(
                command)
        self.run(full_command)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src="source")
        self.copy(pattern="*b2", dst="bin", src="output/bin")
        self.copy(pattern="*b2.exe", dst="bin", src="output/bin")
        self.copy(pattern="*.jam", dst="bin/b2_src", src="output/share/boost-build")

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.env_info.path = [os.path.join(
            self.package_folder, "bin")] + self.env_info.path
        self.env_info.BOOST_BUILD_PATH = os.path.join(
            self.package_folder, "bin", "b2_src", "src", "kernel")
