import os

from conan.tools.files import rename
from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")

    settings = "os", "arch", "compiler", "build_type"
    _sdks = (
        "access-management",
        "accessanalyzer",
        "acm",
        "acm-pca",
        "alexaforbusiness",
        "amp",
        "amplify",
        "amplifybackend",
        "apigateway",
        "apigatewaymanagementapi",
        "apigatewayv2",
        "appconfig",
        "appflow",
        "appintegrations",
        "application-autoscaling",
        "application-insights",
        "appmesh",
        "appstream",
        "appsync",
        "athena",
        "auditmanager",
        "autoscaling",
        "autoscaling-plans",
        "awstransfer",
        "backup",
        "batch",
        "braket",
        "budgets",
        "ce",
        "chime",
        "cloud9",
        "clouddirectory",
        "cloudformation",
        "cloudfront",
        "cloudhsm",
        "cloudhsmv2",
        "cloudsearch",
        "cloudsearchdomain",
        "cloudtrail",
        "codeartifact",
        "codebuild",
        "codecommit",
        "codedeploy",
        "codeguru-reviewer",
        "codeguruprofiler",
        "codepipeline",
        "codestar",
        "codestar-connections",
        "codestar-notifications",
        "cognito-identity",
        "cognito-idp",
        "cognito-sync",
        "comprehend",
        "comprehendmedical",
        "compute-optimizer",
        "config",
        "connect",
        "connect-contact-lens",
        "connectparticipant",
        "cur",
        "customer-profiles",
        "databrew",
        "dataexchange",
        "datapipeline",
        "datasync",
        "dax",
        "detective",
        "devicefarm",
        "devops-guru",
        "directconnect",
        "discovery",
        "dlm",
        "dms",
        "docdb",
        "ds",
        "dynamodb",
        "dynamodbstreams",
        "ebs",
        "ec2",
        "ec2-instance-connect",
        "ecr",
        "ecr-public",
        "ecs",
        "eks",
        "elastic-inference",
        "elasticache",
        "elasticbeanstalk",
        "elasticfilesystem",
        "elasticloadbalancing",
        "elasticloadbalancingv2",
        "elasticmapreduce",
        "elastictranscoder",
        "email",
        "emr-containers",
        "es",
        "eventbridge",
        "events",
        "firehose",
        "fms",
        "forecast",
        "forecastquery",
        "frauddetector",
        "fsx",
        "gamelift",
        "glacier",
        "globalaccelerator",
        "glue",
        "greengrass",
        "greengrassv2",
        "groundstation",
        "guardduty",
        "health",
        "healthlake",
        "honeycode",
        "iam",
        "identity-management",
        "identitystore",
        "imagebuilder",
        "importexport",
        "inspector",
        "iot",
        "iot-data",
        "iot-jobs-data",
        "iot1click-devices",
        "iot1click-projects",
        "iotanalytics",
        "iotdeviceadvisor",
        "iotevents",
        "iotevents-data",
        "iotfleethub",
        "iotsecuretunneling",
        "iotsitewise",
        "iotthingsgraph",
        "iotwireless",
        "ivs",
        "kafka",
        "kendra",
        "kinesis",
        "kinesis-video-archived-media",
        "kinesis-video-media",
        "kinesis-video-signaling",
        "kinesisanalytics",
        "kinesisanalyticsv2",
        "kinesisvideo",
        "kms",
        "lakeformation",
        "lambda",
        "lex",
        "lex-models",
        "lexv2-models",
        "lexv2-runtime",
        "license-manager",
        "lightsail",
        "location",
        "logs",
        "lookoutvision",
        "machinelearning",
        "macie",
        "macie2",
        "managedblockchain",
        "marketplace-catalog",
        "marketplace-entitlement",
        "marketplacecommerceanalytics",
        "mediaconnect",
        "mediaconvert",
        "medialive",
        "mediapackage",
        "mediapackage-vod",
        "mediastore",
        "mediastore-data",
        "mediatailor",
        "meteringmarketplace",
        "migrationhub-config",
        "mobile",
        "mobileanalytics",
        "monitoring",
        "mq",
        "mturk-requester",
        "mwaa",
        "neptune",
        "network-firewall",
        "networkmanager",
        "opsworks",
        "opsworkscm",
        "organizations",
        "outposts",
        "personalize",
        "personalize-events",
        "personalize-runtime",
        "pi",
        "pinpoint",
        "pinpoint-email",
        "polly",
        "polly-sample",
        "pricing",
        "qldb",
        "qldb-session",
        "queues",
        "quicksight",
        "ram",
        "rds",
        "rds-data",
        "redshift",
        "redshift-data",
        "rekognition",
        "resource-groups",
        "resourcegroupstaggingapi",
        "robomaker",
        "route53",
        "route53domains",
        "route53resolver",
        "s3",
        "s3-crt",
        "s3-encryption",
        "s3control",
        "s3outposts",
        "sagemaker",
        "sagemaker-a2i-runtime",
        "sagemaker-edge",
        "sagemaker-featurestore-runtime",
        "sagemaker-runtime",
        "savingsplans",
        "schemas",
        "sdb",
        "secretsmanager",
        "securityhub",
        "serverlessrepo",
        "service-quotas",
        "servicecatalog",
        "servicecatalog-appregistry",
        "servicediscovery",
        "sesv2",
        "shield",
        "signer",
        "sms",
        "sms-voice",
        "snowball",
        "sns",
        "sqs",
        "ssm",
        "sso",
        "sso-admin",
        "sso-oidc",
        "states",
        "storagegateway",
        "sts",
        "support",
        "swf",
        "synthetics",
        "text-to-speech",
        "textract",
        "timestream-query",
        "timestream-write",
        "transcribe",
        "transcribestreaming",
        "transfer",
        "translate",
        "waf",
        "waf-regional",
        "wafv2",
        "wellarchitected",
        "workdocs",
        "worklink",
        "workmail",
        "workmailmessageflow",
        "workspaces",
        "xray",
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{ x: [True, False] for x in _sdks},
    }
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["access-management"] = True
    default_options["identity-management"] = True
    default_options["monitoring"] = True
    default_options["queues"] = True
    default_options["s3-encryption"] = True
    default_options["transfer"] = True
    default_options["text-to-speech"] = True

    generators = "cmake", "cmake_find_package"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _internal_requirements(self):
        return {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"],
        }

    @property
    def _use_aws_crt_cpp(self):
        return tools.scm.Version(self.version) >= "1.9"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.scm.Version(self.version) < "1.9":
            delattr(self.options, "s3-crt")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("aws-c-common/0.6.19")
        if self._use_aws_crt_cpp:
            self.requires("aws-c-cal/0.5.13")
            self.requires("aws-c-http/0.6.13")
            self.requires("aws-c-io/0.10.20")
            self.requires("aws-crt-cpp/0.17.23")
        else:
            self.requires("aws-c-event-stream/0.2.7")
        if self.settings.os != "Windows":
            self.requires("openssl/1.1.1n")
            self.requires("libcurl/7.80.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.get_safe("text-to-speech"):
                self.requires("pulseaudio/14.2")

    def validate(self):
        if (self.options.shared
            and self.settings.compiler == "gcc"
            and tools.scm.Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )
        if (tools.scm.Version(self.version) < "1.9.234"
            and self.settings.compiler == "gcc"
            and tools.scm.Version(self.settings.compiler.version) >= "11.0"
            and self.settings.build_type == "Release"):
            raise ConanInvalidConfiguration(
                "Versions prior to 1.9.234 don't support release builds on >= gcc 11 "
                "See https://github.com/aws/aws-sdk-cpp/issues/1505"
            )
        if self._use_aws_crt_cpp:
            if self._is_msvc and "MT" in msvc_runtime_flag(self):
                raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")
        else:
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                raise ConanInvalidConfiguration(
                    "This version doesn't support arm8. "
                    "See https://github.com/aws/aws-sdk-cpp/issues/1542"
                )

    def package_id(self):
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    setattr(self.info.options, internal_requirement, True)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        build_only = ["core"]
        for sdk in self._sdks:
            if self.options.get_safe(sdk):
                build_only.append(sdk)
        self._cmake.definitions["BUILD_ONLY"] = ";".join(build_only)

        self._cmake.definitions["ENABLE_UNITY_BUILD"] = True
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["AUTORUN_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            self._cmake.definitions["ENABLE_OPENSSL_ENCRYPTION"] = True

        self._cmake.definitions["MINIMIZE_SIZE"] = self.options.min_size
        if self._is_msvc and not self._use_aws_crt_cpp:
            self._cmake.definitions["FORCE_SHARED_CRT"] = "MD" in msvc_runtime_flag(self)

        if tools.build.cross_building(self, self):
            self._cmake.definitions["CURL_HAS_H2_EXITCODE"] = "0"
            self._cmake.definitions["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            self._cmake.definitions["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            self._cmake.definitions["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    @property
    def _res_folder(self):
        return "res"

    def _create_project_cmake_module(self):
        # package files needed to build other components (e.g. aws-cdi-sdk) with this SDK
        for file in [
            "cmake/compiler_settings.cmake",
            "cmake/initialize_project_version.cmake",
            "cmake/utilities.cmake",
            "cmake/sdk_plugin_conf.cmake",
            "toolchains/cmakeProjectConfig.cmake",
            "toolchains/pkg-config.pc.in",
            "aws-cpp-sdk-core/include/aws/core/VersionConfig.h"
        ]:
            self.copy(file, src=self._source_subfolder, dst=self._res_folder)
            tools.files.replace_in_file(self, os.path.join(self.package_folder, self._res_folder, file), "CMAKE_CURRENT_SOURCE_DIR", "AWS_NATIVE_SDK_ROOT", strict=False)

        # avoid getting error from hook
        with tools.files.chdir(self, os.path.join(self.package_folder, self._res_folder)):
            rename(self, os.path.join("toolchains", "cmakeProjectConfig.cmake"), os.path.join("toolchains", "cmakeProjectConf.cmake"))
            tools.files.replace_in_file(self, os.path.join("cmake", "utilities.cmake"), "cmakeProjectConfig.cmake", "cmakeProjectConf.cmake")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self._is_msvc:
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.lib")

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_project_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AWSSDK")

        # core component
        self.cpp_info.components["core"].set_property("cmake_target_name", "AWS::aws-sdk-cpp-core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "aws-sdk-cpp-core")
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = ["aws-c-common::aws-c-common-lib"]
        if self._use_aws_crt_cpp:
            self.cpp_info.components["core"].requires.extend([
                "aws-c-cal::aws-c-cal-lib",
                "aws-c-http::aws-c-http-lib",
                "aws-c-io::aws-c-io-lib",
                "aws-crt-cpp::aws-crt-cpp-lib",
            ])
        else:
            self.cpp_info.components["core"].requires.append("aws-c-event-stream::aws-c-event-stream-lib")

        # other components
        enabled_sdks = [sdk for sdk in self._sdks if self.options.get_safe(sdk)]
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    if internal_requirement not in enabled_sdks:
                        enabled_sdks.append(internal_requirement)

        for sdk in enabled_sdks:
            # TODO: there is no way to properly emulate COMPONENTS names for
            #       find_package(AWSSDK COMPONENTS <sdk>) in set_property()
            #       right now: see https://github.com/conan-io/conan/issues/10258
            self.cpp_info.components[sdk].set_property("cmake_target_name", "AWS::aws-sdk-cpp-{}".format(sdk))
            self.cpp_info.components[sdk].set_property("pkg_config_name", "aws-sdk-cpp-{}".format(sdk))
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[sdk].names["cmake_find_package"] = "aws-sdk-cpp-" + sdk
            self.cpp_info.components[sdk].names["cmake_find_package_multi"] = "aws-sdk-cpp-" + sdk
            component_alias = "aws-sdk-cpp-{}_alias".format(sdk) # to emulate COMPONENTS names for find_package()
            self.cpp_info.components[component_alias].names["cmake_find_package"] = sdk
            self.cpp_info.components[component_alias].names["cmake_find_package_multi"] = sdk
            self.cpp_info.components[component_alias].requires = [sdk]

        # specific system_libs, frameworks and requires of components
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs.extend([
                "winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"
            ])
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].system_libs.append("winmm")
        else:
            self.cpp_info.components["core"].requires.extend(["libcurl::curl", "openssl::openssl"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("atomic")
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].requires.append("pulseaudio::pulseaudio")

        if self.settings.os == "Macos":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].frameworks.append("CoreAudio")

        lib_stdcpp = tools.stdcpp_library(self)
        if lib_stdcpp:
            self.cpp_info.components["core"].system_libs.append(lib_stdcpp)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "AWSSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "AWSSDK"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["core"].names["cmake_find_package"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "aws-sdk-cpp-core"

        self.cpp_info.components["plugin_scripts"].requires = ["core"]
        self.cpp_info.components["plugin_scripts"].builddirs.extend([
            os.path.join(self._res_folder, "cmake"),
            os.path.join(self._res_folder, "toolchains")])
        self.cpp_info.components["plugin_scripts"].build_modules.append(os.path.join(self._res_folder, "cmake", "sdk_plugin_conf.cmake"))
