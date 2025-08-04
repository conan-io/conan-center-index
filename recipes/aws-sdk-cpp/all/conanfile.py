import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2"


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # This list comes from tools/code-generation/api-description, which then generates the sdk sources
    # To generate for a new one, run the build once and check src/generated/src inside your build_folder, remove the common aws-sdk-cpp prefix
    # NON_GENERATED_CLIENT_LIST in src/cmake/sdks.cmake contains extra ones that should also be added here
    # and that's the list of sdks. Then join it to this one
    _sdks = (
        ('AWSMigrationHub', '1.11.618'),
        ('access-management', '1.11.618'),
        ('accessanalyzer', '1.11.618'),
        ('account', '1.11.618'),
        ('acm', '1.11.618'),
        ('acm-pca', '1.11.618'),
        ('aiops', '1.11.618'),
        ('amp', '1.11.618'),
        ('amplify', '1.11.618'),
        ('amplifybackend', '1.11.618'),
        ('amplifyuibuilder', '1.11.618'),
        ('apigateway', '1.11.618'),
        ('apigatewaymanagementapi', '1.11.618'),
        ('apigatewayv2', '1.11.618'),
        ('appconfig', '1.11.618'),
        ('appconfigdata', '1.11.618'),
        ('appfabric', '1.11.618'),
        ('appflow', '1.11.618'),
        ('appintegrations', '1.11.618'),
        ('application-autoscaling', '1.11.618'),
        ('application-insights', '1.11.618'),
        ('application-signals', '1.11.618'),
        ('applicationcostprofiler', '1.11.618'),
        ('appmesh', '1.11.618'),
        ('apprunner', '1.11.618'),
        ('appstream', '1.11.618'),
        ('appsync', '1.11.618'),
        ('apptest', '1.11.618'),
        ('arc-zonal-shift', '1.11.618'),
        ('artifact', '1.11.618'),
        ('athena', '1.11.618'),
        ('auditmanager', '1.11.618'),
        ('autoscaling', '1.11.618'),
        ('autoscaling-plans', '1.11.618'),
        ('awstransfer', '1.11.618'),
        ('b2bi', '1.11.618'),
        ('backup', '1.11.618'),
        ('backup-gateway', '1.11.618'),
        ('backupsearch', '1.11.618'),
        ('batch', '1.11.618'),
        ('bcm-data-exports', '1.11.618'),
        ('bcm-pricing-calculator', '1.11.618'),
        ('bedrock', '1.11.618'),
        ('bedrock-agent', '1.11.618'),
        ('bedrock-agent-runtime', '1.11.618'),
        ('bedrock-data-automation', '1.11.618'),
        ('bedrock-data-automation-runtime', '1.11.618'),
        ('bedrock-runtime', '1.11.618'),
        ('billing', '1.11.618'),
        ('billingconductor', '1.11.618'),
        ('braket', '1.11.618'),
        ('budgets', '1.11.618'),
        ('ce', '1.11.618'),
        ('chatbot', '1.11.618'),
        ('chime', '1.11.618'),
        ('chime-sdk-identity', '1.11.618'),
        ('chime-sdk-media-pipelines', '1.11.618'),
        ('chime-sdk-meetings', '1.11.618'),
        ('chime-sdk-messaging', '1.11.618'),
        ('chime-sdk-voice', '1.11.618'),
        ('cleanrooms', '1.11.618'),
        ('cleanroomsml', '1.11.618'),
        ('cloud9', '1.11.618'),
        ('cloudcontrol', '1.11.618'),
        ('clouddirectory', '1.11.618'),
        ('cloudformation', '1.11.618'),
        ('cloudfront', '1.11.618'),
        ('cloudfront-keyvaluestore', '1.11.618'),
        ('cloudhsm', '1.11.618'),
        ('cloudhsmv2', '1.11.618'),
        ('cloudsearch', '1.11.618'),
        ('cloudsearchdomain', '1.11.618'),
        ('cloudtrail', '1.11.618'),
        ('cloudtrail-data', '1.11.618'),
        ('codeartifact', '1.11.618'),
        ('codebuild', '1.11.618'),
        ('codecatalyst', '1.11.618'),
        ('codecommit', '1.11.618'),
        ('codeconnections', '1.11.618'),
        ('codedeploy', '1.11.618'),
        ('codeguru-reviewer', '1.11.618'),
        ('codeguru-security', '1.11.618'),
        ('codeguruprofiler', '1.11.618'),
        ('codepipeline', '1.11.618'),
        ('codestar-connections', '1.11.618'),
        ('codestar-notifications', '1.11.618'),
        ('cognito-identity', '1.11.618'),
        ('cognito-idp', '1.11.618'),
        ('cognito-sync', '1.11.618'),
        ('comprehend', '1.11.618'),
        ('comprehendmedical', '1.11.618'),
        ('compute-optimizer', '1.11.618'),
        ('config', '1.11.618'),
        ('connect', '1.11.618'),
        ('connect-contact-lens', '1.11.618'),
        ('connectcampaigns', '1.11.618'),
        ('connectcampaignsv2', '1.11.618'),
        ('connectcases', '1.11.618'),
        ('connectparticipant', '1.11.618'),
        ('controlcatalog', '1.11.618'),
        ('controltower', '1.11.618'),
        ('cost-optimization-hub', '1.11.618'),
        ('cur', '1.11.618'),
        ('customer-profiles', '1.11.618'),
        ('databrew', '1.11.618'),
        ('dataexchange', '1.11.618'),
        ('datapipeline', '1.11.618'),
        ('datasync', '1.11.618'),
        ('datazone', '1.11.618'),
        ('dax', '1.11.618'),
        ('deadline', '1.11.618'),
        ('detective', '1.11.618'),
        ('devicefarm', '1.11.618'),
        ('devops-guru', '1.11.618'),
        ('directconnect', '1.11.618'),
        ('directory-service-data', '1.11.618'),
        ('discovery', '1.11.618'),
        ('dlm', '1.11.618'),
        ('dms', '1.11.618'),
        ('docdb', '1.11.618'),
        ('docdb-elastic', '1.11.618'),
        ('drs', '1.11.618'),
        ('ds', '1.11.618'),
        ('dsql', '1.11.618'),
        ('dynamodb', '1.11.618'),
        ('dynamodbstreams', '1.11.618'),
        ('ebs', '1.11.618'),
        ('ec2', '1.11.618'),
        ('ec2-instance-connect', '1.11.618'),
        ('ecr', '1.11.618'),
        ('ecr-public', '1.11.618'),
        ('ecs', '1.11.618'),
        ('eks', '1.11.618'),
        ('eks-auth', '1.11.618'),
        ('elasticache', '1.11.618'),
        ('elasticbeanstalk', '1.11.618'),
        ('elasticfilesystem', '1.11.618'),
        ('elasticloadbalancing', '1.11.618'),
        ('elasticloadbalancingv2', '1.11.618'),
        ('elasticmapreduce', '1.11.618'),
        ('elastictranscoder', '1.11.618'),
        ('email', '1.11.618'),
        ('emr-containers', '1.11.618'),
        ('emr-serverless', '1.11.618'),
        ('entityresolution', '1.11.618'),
        ('es', '1.11.618'),
        ('eventbridge', '1.11.618'),
        ('events', '1.11.618'),
        ('evidently', '1.11.618'),
        ('evs', '1.11.618'),
        ('finspace', '1.11.618'),
        ('finspace-data', '1.11.618'),
        ('firehose', '1.11.618'),
        ('fis', '1.11.618'),
        ('fms', '1.11.618'),
        ('forecast', '1.11.618'),
        ('forecastquery', '1.11.618'),
        ('frauddetector', '1.11.618'),
        ('freetier', '1.11.618'),
        ('fsx', '1.11.618'),
        ('gamelift', '1.11.618'),
        ('gameliftstreams', '1.11.618'),
        ('geo-maps', '1.11.618'),
        ('geo-places', '1.11.618'),
        ('geo-routes', '1.11.618'),
        ('glacier', '1.11.618'),
        ('globalaccelerator', '1.11.618'),
        ('glue', '1.11.618'),
        ('grafana', '1.11.618'),
        ('greengrass', '1.11.618'),
        ('greengrassv2', '1.11.618'),
        ('groundstation', '1.11.618'),
        ('guardduty', '1.11.618'),
        ('health', '1.11.618'),
        ('healthlake', '1.11.618'),
        ('iam', '1.11.618'),
        ('identity-management', '1.11.618'),
        ('identitystore', '1.11.618'),
        ('imagebuilder', '1.11.618'),
        ('importexport', '1.11.618'),
        ('inspector', '1.11.618'),
        ('inspector-scan', '1.11.618'),
        ('inspector2', '1.11.618'),
        ('internetmonitor', '1.11.618'),
        ('invoicing', '1.11.618'),
        ('iot', '1.11.618'),
        ('iot-data', '1.11.618'),
        ('iot-jobs-data', '1.11.618'),
        ('iot-managed-integrations', '1.11.618'),
        ('iot1click-devices', '1.11.618'),
        ('iot1click-projects', '1.11.618'),
        ('iotanalytics', '1.11.618'),
        ('iotdeviceadvisor', '1.11.618'),
        ('iotevents', '1.11.618'),
        ('iotevents-data', '1.11.618'),
        ('iotfleethub', '1.11.618'),
        ('iotfleetwise', '1.11.618'),
        ('iotsecuretunneling', '1.11.618'),
        ('iotsitewise', '1.11.618'),
        ('iotthingsgraph', '1.11.618'),
        ('iottwinmaker', '1.11.618'),
        ('iotwireless', '1.11.618'),
        ('ivs', '1.11.618'),
        ('ivs-realtime', '1.11.618'),
        ('ivschat', '1.11.618'),
        ('kafka', '1.11.618'),
        ('kafkaconnect', '1.11.618'),
        ('kendra', '1.11.618'),
        ('kendra-ranking', '1.11.618'),
        ('keyspaces', '1.11.618'),
        ('keyspacesstreams', '1.11.618'),
        ('kinesis', '1.11.618'),
        ('kinesis-video-archived-media', '1.11.618'),
        ('kinesis-video-media', '1.11.618'),
        ('kinesis-video-signaling', '1.11.618'),
        ('kinesis-video-webrtc-storage', '1.11.618'),
        ('kinesisanalytics', '1.11.618'),
        ('kinesisanalyticsv2', '1.11.618'),
        ('kinesisvideo', '1.11.618'),
        ('kms', '1.11.618'),
        ('lakeformation', '1.11.618'),
        ('lambda', '1.11.618'),
        ('launch-wizard', '1.11.618'),
        ('lex', '1.11.618'),
        ('lex-models', '1.11.618'),
        ('lexv2-models', '1.11.618'),
        ('lexv2-runtime', '1.11.618'),
        ('license-manager', '1.11.618'),
        ('license-manager-linux-subscriptions', '1.11.618'),
        ('license-manager-user-subscriptions', '1.11.618'),
        ('lightsail', '1.11.618'),
        ('location', '1.11.618'),
        ('logs', '1.11.618'),
        ('lookoutequipment', '1.11.618'),
        ('lookoutmetrics', '1.11.618'),
        ('lookoutvision', '1.11.618'),
        ('m2', '1.11.618'),
        ('machinelearning', '1.11.618'),
        ('macie2', '1.11.618'),
        ('mailmanager', '1.11.618'),
        ('managedblockchain', '1.11.618'),
        ('managedblockchain-query', '1.11.618'),
        ('marketplace-agreement', '1.11.618'),
        ('marketplace-catalog', '1.11.618'),
        ('marketplace-deployment', '1.11.618'),
        ('marketplace-entitlement', '1.11.618'),
        ('marketplace-reporting', '1.11.618'),
        ('marketplacecommerceanalytics', '1.11.618'),
        ('mediaconnect', '1.11.618'),
        ('mediaconvert', '1.11.618'),
        ('medialive', '1.11.618'),
        ('mediapackage', '1.11.618'),
        ('mediapackage-vod', '1.11.618'),
        ('mediapackagev2', '1.11.618'),
        ('mediastore', '1.11.618'),
        ('mediastore-data', '1.11.618'),
        ('mediatailor', '1.11.618'),
        ('medical-imaging', '1.11.618'),
        ('memorydb', '1.11.618'),
        ('meteringmarketplace', '1.11.618'),
        ('mgn', '1.11.618'),
        ('migration-hub-refactor-spaces', '1.11.618'),
        ('migrationhub-config', '1.11.618'),
        ('migrationhuborchestrator', '1.11.618'),
        ('migrationhubstrategy', '1.11.618'),
        ('monitoring', '1.11.618'),
        ('mpa', '1.11.618'),
        ('mq', '1.11.618'),
        ('mturk-requester', '1.11.618'),
        ('mwaa', '1.11.618'),
        ('neptune', '1.11.618'),
        ('neptune-graph', '1.11.618'),
        ('neptunedata', '1.11.618'),
        ('network-firewall', '1.11.618'),
        ('networkflowmonitor', '1.11.618'),
        ('networkmanager', '1.11.618'),
        ('networkmonitor', '1.11.618'),
        ('notifications', '1.11.618'),
        ('notificationscontacts', '1.11.618'),
        ('oam', '1.11.618'),
        ('observabilityadmin', '1.11.618'),
        ('omics', '1.11.618'),
        ('opensearch', '1.11.618'),
        ('opensearchserverless', '1.11.618'),
        ('opsworks', '1.11.618'),
        ('opsworkscm', '1.11.618'),
        ('organizations', '1.11.618'),
        ('osis', '1.11.618'),
        ('outposts', '1.11.618'),
        ('panorama', '1.11.618'),
        ('partnercentral-selling', '1.11.618'),
        ('payment-cryptography', '1.11.618'),
        ('payment-cryptography-data', '1.11.618'),
        ('pca-connector-ad', '1.11.618'),
        ('pca-connector-scep', '1.11.618'),
        ('pcs', '1.11.618'),
        ('personalize', '1.11.618'),
        ('personalize-events', '1.11.618'),
        ('personalize-runtime', '1.11.618'),
        ('pi', '1.11.618'),
        ('pinpoint', '1.11.618'),
        ('pinpoint-email', '1.11.618'),
        ('pinpoint-sms-voice-v2', '1.11.618'),
        ('pipes', '1.11.618'),
        ('polly', '1.11.618'),
        ('pricing', '1.11.618'),
        ('proton', '1.11.618'),
        ('qapps', '1.11.618'),
        ('qbusiness', '1.11.618'),
        ('qconnect', '1.11.618'),
        ('qldb', '1.11.618'),
        ('qldb-session', '1.11.618'),
        ('quicksight', '1.11.618'),
        ('ram', '1.11.618'),
        ('rbin', '1.11.618'),
        ('rds', '1.11.618'),
        ('rds-data', '1.11.618'),
        ('redshift', '1.11.618'),
        ('redshift-data', '1.11.618'),
        ('redshift-serverless', '1.11.618'),
        ('rekognition', '1.11.618'),
        ('repostspace', '1.11.618'),
        ('resiliencehub', '1.11.618'),
        ('resource-explorer-2', '1.11.618'),
        ('resource-groups', '1.11.618'),
        ('resourcegroupstaggingapi', '1.11.618'),
        ('robomaker', '1.11.618'),
        ('rolesanywhere', '1.11.618'),
        ('route53', '1.11.618'),
        ('route53-recovery-cluster', '1.11.618'),
        ('route53-recovery-control-config', '1.11.618'),
        ('route53-recovery-readiness', '1.11.618'),
        ('route53domains', '1.11.618'),
        ('route53profiles', '1.11.618'),
        ('route53resolver', '1.11.618'),
        ('rum', '1.11.618'),
        ('s3', '1.11.618'),
        ('s3-crt', '1.11.618'),
        ('s3-encryption', '1.11.618'),
        ('s3control', '1.11.618'),
        ('s3outposts', '1.11.618'),
        ('s3tables', '1.11.618'),
        ('sagemaker', '1.11.618'),
        ('sagemaker-a2i-runtime', '1.11.618'),
        ('sagemaker-edge', '1.11.618'),
        ('sagemaker-featurestore-runtime', '1.11.618'),
        ('sagemaker-geospatial', '1.11.618'),
        ('sagemaker-metrics', '1.11.618'),
        ('sagemaker-runtime', '1.11.618'),
        ('savingsplans', '1.11.618'),
        ('scheduler', '1.11.618'),
        ('schemas', '1.11.618'),
        ('sdb', '1.11.618'),
        ('secretsmanager', '1.11.618'),
        ('security-ir', '1.11.618'),
        ('securityhub', '1.11.618'),
        ('securitylake', '1.11.618'),
        ('serverlessrepo', '1.11.618'),
        ('service-quotas', '1.11.618'),
        ('servicecatalog', '1.11.618'),
        ('servicecatalog-appregistry', '1.11.618'),
        ('servicediscovery', '1.11.618'),
        ('sesv2', '1.11.618'),
        ('shield', '1.11.618'),
        ('signer', '1.11.618'),
        ('simspaceweaver', '1.11.618'),
        ('sms', '1.11.618'),
        ('sms-voice', '1.11.618'),
        ('snow-device-management', '1.11.618'),
        ('snowball', '1.11.618'),
        ('sns', '1.11.618'),
        ('socialmessaging', '1.11.618'),
        ('sqs', '1.11.618'),
        ('ssm', '1.11.618'),
        ('ssm-contacts', '1.11.618'),
        ('ssm-guiconnect', '1.11.618'),
        ('ssm-incidents', '1.11.618'),
        ('ssm-quicksetup', '1.11.618'),
        ('ssm-sap', '1.11.618'),
        ('sso', '1.11.618'),
        ('sso-admin', '1.11.618'),
        ('sso-oidc', '1.11.618'),
        ('states', '1.11.618'),
        ('storagegateway', '1.11.618'),
        ('sts', '1.11.618'),
        ('supplychain', '1.11.618'),
        ('support', '1.11.618'),
        ('support-app', '1.11.618'),
        ('swf', '1.11.618'),
        ('synthetics', '1.11.618'),
        ('taxsettings', '1.11.618'),
        ('text-to-speech', '1.11.618'),
        ('textract', '1.11.618'),
        ('timestream-influxdb', '1.11.618'),
        ('timestream-query', '1.11.618'),
        ('timestream-write', '1.11.618'),
        ('tnb', '1.11.618'),
        ('transcribe', '1.11.618'),
        ('transcribestreaming', '1.11.618'),
        ('transfer', '1.11.618'),
        ('translate', '1.11.618'),
        ('trustedadvisor', '1.11.618'),
        ('verifiedpermissions', '1.11.618'),
        ('voice-id', '1.11.618'),
        ('vpc-lattice', '1.11.618'),
        ('waf', '1.11.618'),
        ('waf-regional', '1.11.618'),
        ('wafv2', '1.11.618'),
        ('wellarchitected', '1.11.618'),
        ('wisdom', '1.11.618'),
        ('workdocs', '1.11.618'),
        ('worklink', '1.11.618'),
        ('workmail', '1.11.618'),
        ('workmailmessageflow', '1.11.618'),
        ('workspaces', '1.11.618'),
        ('workspaces-instances', '1.11.618'),
        ('workspaces-thin-client', '1.11.618'),
        ('workspaces-web', '1.11.618'),
        ('xray', '1.11.618'),
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{sdk_name: [None, True, False] for sdk_name, _ in _sdks},
    }
    default_options = {
        **{
            "shared": False,
            "fPIC": True,
            "min_size": False
        },
        **{sdk_name: None for sdk_name, _ in _sdks},
        # Overrides
        "monitoring": True  # TODO: Clarify why monitoring is True by default
    }

    short_paths = True

    @property
    def _internal_requirements(self):
        # These modules and dependencies come from https://github.com/aws/aws-sdk-cpp/blob/1.11.352/cmake/sdksCommon.cmake#L147 and below
        # Additionally Core is added to all modules automatically
        return {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"],
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # Main modules are true by default, but the user can set them to false
        for module in self._internal_requirements:
            setattr(self.options, module, True)

        # Remove all sdk options not belonging to the current version
        for sdk_name, sdk_versions in self._sdks:
            if self.version not in sdk_versions:
                self.options.rm_safe(sdk_name)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # If the user does not specify a value for a specific sdk:
        # - Set it to True if it's a dependency of a main module that is set to True
        for module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(module):
                for dependency in dependencies:
                    # Don't listen to the linter, get_safe should be compared like this to None
                    # TODO: Remove str comparison when Conan 1 is disabled
                    if str(self.options.get_safe(dependency)) == "None":
                        setattr(self.options, dependency, True)

        # - Otherwise set it to False
        # This way there are no None options past this method, and we can control default values
        # of the dependencies of the main modules but still give the user control over them
        for sdk_name, sdk_versions in self._sdks:
            # == None is true for both "was deleted" and "was not set by the user",
            # ensure we only try to set the value to false for the latter
            if self.version in sdk_versions and self.options.get_safe(sdk_name) == None:
                setattr(self.options, sdk_name, False)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # These versions come from prefetch_crt_dependency.sh,
        # dont bump them independently, check the file
        # Create the new versions for the dependencies in the order shown
        # in that script, they are mostly topo sorted
        self.requires("aws-crt-cpp/0.32.8", transitive_headers=True)
        self.requires("aws-c-auth/0.9.0")
        self.requires("aws-c-cal/0.9.1")
        self.requires("aws-c-common/0.12.3")
        self.requires("aws-c-compression/0.3.1")
        self.requires("aws-c-event-stream/0.5.4")
        self.requires("aws-c-http/0.10.1")
        self.requires("aws-c-io/0.19.1")
        self.requires("aws-c-mqtt/0.13.1")
        if self.options.get_safe("s3-crt"):
            self.requires("aws-c-s3/0.8.0")
        self.requires("aws-c-sdkutils/0.2.4")  # No mention of this in the code
        self.requires("aws-checksums/0.2.6")
        if self.settings.os != "Windows":
            # Used transitively in core/utils/crypto/openssl/CryptoImpl.h public header
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
            # Used transitively in core/http/curl/CurlHandleContainer.h public header
            self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)
        if self.settings.os == "Linux":
            # Pulseaudio -> libcap, libalsa only support linux, don't use pulseaudio on other platforms
            if self.options.get_safe("text-to-speech"):
                # Used transitively in text-to-speech/PulseAudioPCMOutputDriver.h public header
                self.requires("pulseaudio/14.2", transitive_headers=True, transitive_libs=True)
        # zlib is used if ENABLE_ZLIB_REQUEST_COMPRESSION is enabled, set ot ON by default
        self.requires("zlib/[>=1.2.11 <2]")

    def validate_build(self):
        if self.settings_build.os == "Windows" and self.settings.os == "Android":
            raise ConanInvalidConfiguration("Cross-building from Windows to Android is not supported")

        if (self.options.shared
                and self.settings.compiler == "gcc"
                and Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )

    def validate(self):
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")
        if (is_msvc(self) and self.options.shared
                and not self.dependencies["aws-c-common"].options.shared):
            raise ConanInvalidConfiguration(f"{self.ref} with shared is not supported with aws-c-common static")

        # If the user has explicitly set a main module dependency to False,
        # error out if the main module itself is not also disabled
        for main_module, dependencies in self._internal_requirements.items():
            if self.options.get_safe(main_module):
                for internal_requirement in dependencies:
                    if not self.options.get_safe(internal_requirement):
                        raise ConanInvalidConfiguration(f"-o={self.ref}:{main_module}=True requires -o={self.ref}:{internal_requirement}=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def _enabled_sdks(self):
        for sdk in self._sdks:
            if self.options.get_safe(sdk[0]):
                yield sdk

    def generate(self):
        tc = CMakeToolchain(self)
        # All option() are defined before project() in upstream CMakeLists,
        # therefore we must use cache_variables

        build_only = ["core"]
        for sdk_name, _ in self._enabled_sdks():
            build_only.append(sdk_name)
        tc.cache_variables["BUILD_ONLY"] = ";".join(build_only)

        tc.cache_variables["ENABLE_UNITY_BUILD"] = True
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["AUTORUN_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            tc.cache_variables["USE_OPENSSL"] = True
            tc.cache_variables["ENABLE_OPENSSL_ENCRYPTION"] = True

        tc.cache_variables["MINIMIZE_SIZE"] = self.options.min_size
        if is_msvc(self):
            tc.cache_variables["FORCE_SHARED_CRT"] = not is_msvc_static_runtime(self)

        if cross_building(self):
            tc.cache_variables["CURL_HAS_H2_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        if is_msvc(self):
            tc.preprocessor_definitions["_SILENCE_CXX17_OLD_ALLOCATOR_MEMBERS_DEPRECATION_WARNING"] = "1"
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _res_folder(self):
        return "res"

    def _create_project_cmake_module(self):
        # package files needed to build other components (e.g. aws-cdi-sdk) with this SDK
        dependant_files = [
            "cmake/compiler_settings.cmake",
            "cmake/initialize_project_version.cmake",
            "cmake/utilities.cmake",
            "cmake/sdk_plugin_conf.cmake",
            "toolchains/cmakeProjectConfig.cmake",
            "toolchains/pkg-config.pc.in"
        ]
        dependant_files.append("src/aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        for file in dependant_files:
            copy(self, file, src=self.source_folder, dst=os.path.join(self.package_folder, self._res_folder))
            replace_in_file(
                self, os.path.join(self.package_folder, self._res_folder, file),
                "CMAKE_CURRENT_SOURCE_DIR", "AWS_NATIVE_SDK_ROOT",
                strict=False,
            )

        # avoid getting error from hook
        rename(self, os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConfig.cmake"),
               os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConf.cmake"))
        replace_in_file(
            self, os.path.join(self.package_folder, self._res_folder, "cmake", "utilities.cmake"),
            "cmakeProjectConfig.cmake", "cmakeProjectConf.cmake",
        )

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if is_msvc(self):
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            rm(self, "*.lib", os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_project_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AWSSDK")

        sdk_plugin_conf = os.path.join(self._res_folder, "cmake", "sdk_plugin_conf.cmake")
        self.cpp_info.set_property("cmake_build_modules", [sdk_plugin_conf])

        # core component
        self.cpp_info.components["core"].set_property("cmake_target_name", "AWS::aws-sdk-cpp-core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "aws-sdk-cpp-core")
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = [
            "aws-crt-cpp::aws-crt-cpp",
            "aws-c-auth::aws-c-auth",
            "aws-c-cal::aws-c-cal",
            "aws-c-common::aws-c-common",
            "aws-c-compression::aws-c-compression",
            "aws-c-event-stream::aws-c-event-stream",
            "aws-c-http::aws-c-http",
            "aws-c-io::aws-c-io",
            "aws-c-mqtt::aws-c-mqtt",
            "aws-checksums::aws-checksums",
            "zlib::zlib"
        ]

        self.cpp_info.components["core"].requires.extend([
            "aws-c-sdkutils::aws-c-sdkutils",
        ])

        # TODO: We might want to set cmake_components if the targets dont match the component names
        for sdk, _ in self._enabled_sdks():
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"AWS::aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].set_property("pkg_config_name", f"aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: Remove, Conan 1 legacy, but this component now exists, it's part of the api
            component_alias = f"aws-sdk-cpp-{sdk}_alias"  # to emulate COMPONENTS names for find_package()
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

        if self.settings.os == "Linux":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].requires.append("pulseaudio::pulseaudio")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("atomic")

        if self.options.get_safe("s3-crt"):
            self.cpp_info.components["s3-crt"].requires.append("aws-c-s3::aws-c-s3")

        if self.settings.os == "Macos":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].frameworks.extend(["CoreAudio", "AudioToolbox"])

        libcxx = stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["core"].system_libs.append(libcxx)

        self.cpp_info.components["plugin_scripts"].requires = ["core"]
        self.cpp_info.components["plugin_scripts"].builddirs.extend([
            os.path.join(self._res_folder, "cmake"),
            os.path.join(self._res_folder, "toolchains")])
