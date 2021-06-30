import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conans.client.build.cmake_flags import get_generator


class OnnxRuntimeConan(ConanFile):
    name = "onnxruntime"
    description = """ONNX Runtime is an accelerator for machine learning models with multi platform support and a 
                     flexible interface to integrate with hardware-specific libraries. ONNX Runtime can be used with 
                     models from PyTorch, Tensorflow/Keras, TFLite, scikit-learn, and other frameworks."""
    topics = ("conan", "onnxruntime")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.onnxruntime.ai/"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    repo_url = "https://github.com/Microsoft/onnxruntime"

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _build_subfolder(self):
        return os.path.join(self.source_folder, "build_subfolder")

    def source(self):
        git_version = tools.Git.get_version()
        target_revision = self.conan_data['sources'][self.version]['revision']
        if git_version > "2.5.0":
            git = tools.Git(folder=self._source_subfolder)
            git.clone(url=self.repo_url)
            git.checkout(element=target_revision, submodule='recursive')
        else:
            self.run(f'git clone --recursive {self.repo_url} {self._source_subfolder}')
            self.run(f'cd {self._source_subfolder} && git checkout {target_revision}')
            self.run(f'cd {self._source_subfolder} && git submodule sync')

    def build(self):
        build_type = self.settings.get_safe("build_type", default="Release")
        build_script = os.path.join(self._source_subfolder, "tools", "ci_build", "build.py")
        args = ['--build_dir', self._build_subfolder]
        args += ['--config', build_type]
        args += ['--build_shared_lib']
        args += ['--parallel']
        args += ['--skip_tests']
        args += ['--skip_submodule_sync']
        args += ['--cmake_extra_defines', f'CMAKE_INSTALL_PREFIX={self.package_folder}']
        if tools.os_info.is_windows:
            args += ['--cmake_generator', f'\"{get_generator(self)}\"']
        args = ' '.join(args)
        self.run(f"python3 {build_script} {args}")
        cmake = CMake(self)
        cmake.install(build_dir=os.path.join(self._build_subfolder, build_type))

    def package(self):
        if tools.os_info.is_windows:
            os.remove(os.path.join(self.package_folder, "bin", "onnx_test_runner.exe"))
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))
