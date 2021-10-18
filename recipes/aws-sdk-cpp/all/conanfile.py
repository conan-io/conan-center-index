from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    _sdks = ("access-management",
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
            "xray"
           )
    options = {
            **{ x: [True, False] for x in _sdks},
            **{
                "shared": [True, False],
                "fPIC": [True, False],
                "min_size": [True, False],
                }
            }
    default_options = {key: False for key in options.keys()}
    default_options["access-management"] = True
    default_options["fPIC"] = True
    default_options["identity-management"] = True
    default_options["monitoring"] = True
    default_options["queues"] = True
    default_options["s3-encryption"] = True
    default_options["transfer"] = True
    default_options["text-to-speech"] = True
    _internal_requirements = {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"]
            }

    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _use_aws_crt_cpp(self):
        return tools.Version(self.version) >= "1.9"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if (self.options.shared
            and self.settings.compiler == "gcc"
            and tools.Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration("""Doesn't support gcc5 / shared.
                See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744""")
        if self._use_aws_crt_cpp:
            if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")
        else:
            if (self.settings.os == "Macos"
                    and self.settings.arch == "armv8"):
                raise ConanInvalidConfiguration("""This version doesn't support arm8
                    See https://github.com/aws/aws-sdk-cpp/issues/1542""")

    def requirements(self):
        self.requires("aws-c-common/0.6.9")
        if self._use_aws_crt_cpp:
            self.requires("aws-c-cal/0.5.12")
            self.requires("aws-c-io/0.10.9")
            self.requires("aws-crt-cpp/0.14.3")
        else:
            self.requires("aws-c-event-stream/0.1.5")
        if self.settings.os != "Windows":
            self.requires("openssl/1.1.1l")
            self.requires("libcurl/7.78.0")
        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.get_safe("text-to-speech"):
                self.requires("pulseaudio/14.2")

    def package_id(self):
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    setattr(self.info.options, internal_requirement, True)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        build_only = ["core"]
        for sdk in self._sdks:
            if getattr(self.options, sdk):
                build_only.append(sdk)
        self._cmake.definitions["BUILD_ONLY"] = ";".join(build_only)

        self._cmake.definitions["ENABLE_UNITY_BUILD"] = True
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["AUTORUN_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_DEPS"] = False

        self._cmake.definitions["MINIMIZE_SIZE"] = self.options.min_size
        if self.settings.compiler == "Visual Studio" and not self._use_aws_crt_cpp:
            self._cmake.definitions["FORCE_SHARED_CRT"] = "MD" in self.settings.compiler.runtime

        if tools.cross_building(self):
            self._cmake.definitions["CURL_HAS_H2_EXITCODE"] = "0"
            self._cmake.definitions["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            self._cmake.definitions["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            self._cmake.definitions["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.lib")

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "AWSSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "AWSSDK"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["core"].names["cmake_find_package"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].names["pkg_config"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = ["aws-c-common::aws-c-common-lib"]
        if self._use_aws_crt_cpp:
            self.cpp_info.components["core"].requires.extend([
                "aws-c-io::aws-c-io-lib",
                "aws-c-cal::aws-c-cal-lib",
                "aws-crt-cpp::aws-crt-cpp-lib",
            ])
        else:
            self.cpp_info.components["core"].requires.append("aws-c-event-stream::aws-c-event-stream-lib")

        enabled_sdks = [sdk for sdk in self._sdks if getattr(self.options, sdk)]
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    if internal_requirement not in enabled_sdks:
                        enabled_sdks.append(internal_requirement)

        for sdk in enabled_sdks:
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]
            self.cpp_info.components[sdk].names["cmake_find_package"] = "aws-sdk-cpp-" + sdk
            self.cpp_info.components[sdk].names["cmake_find_package_multi"] = "aws-sdk-cpp-" + sdk
            self.cpp_info.components[sdk].names["pkg_config"] = "aws-sdk-cpp-" + sdk

            # alias name to support find_package(AWSSDK COMPONENTS s3 kms ...)
            component_alias = "aws-sdk-cpp-{}_alias".format(sdk)
            self.cpp_info.components[component_alias].names["cmake_find_package"] = sdk
            self.cpp_info.components[component_alias].names["cmake_find_package_multi"] = sdk
            self.cpp_info.components[component_alias].requires = [sdk]

        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs.extend(["winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"])
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

