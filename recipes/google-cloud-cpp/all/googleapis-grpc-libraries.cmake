cmake_minimum_required(VERSION 3.7)
# google-cloud-cpp consume some protos generated with the grpc_cpp_plugin,
# these protos (as header + library) are not available in googleapis package,
# so we need to generate them here.
#
# Approach here is to generate required grpc-protos, build them into some
# targets, transitively link googleapis libraries and use those targets
# in the google-cloud-cpp project (with the same names they had when vendored).
#
# Depending on the 'googleapis' versions, some protos might be moved from vXbetaY
# folders to vX stable ones... or some protos might be available or not in
# libraries provided by 'googleapis'. Those that are not available are also included
# in the targets generated here

set(_gRPC_PROTO_GENS_DIR ${CMAKE_BINARY_DIR})
file(MAKE_DIRECTORY ${_gRPC_PROTO_GENS_DIR})
set(GOOGLEAPIS_GRPC_PROTOS_TARGETS "")

include(CompileProtos)
include(googleapis-helpers.cmake)

# Libraries that are consumed by other targets in `google-cloud-cpp`
googleapis_grpc_proto_library(iam_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/admin"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/credentials"
    )
googleapis_grpc_proto_library(iam_v1_policy_protos 
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/v1/iam_policy.proto"
    )
googleapis_grpc_proto_library(longrunning_operations_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/longrunning"
    )
googleapis_grpc_proto_library(rpc_error_details_protos 
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/rpc/error_details.proto"
    )
googleapis_grpc_proto_library(rpc_status_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/rpc/status.proto"
    )
googleapis_grpc_proto_library(bigtable_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/bigtable"
    )
googleapis_grpc_proto_library(cloud_bigquery_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery" 
    PROTOS 
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/connection/v1beta1/connection.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/assessment_task.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_entities.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_error_details.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_metrics.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/translation_task.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/migration_service.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/migration/v2alpha/translation_service.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/bigquery/reservation/v1beta1/reservation.proto"
        )
googleapis_grpc_proto_library(logging_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/logging"
    )
googleapis_grpc_proto_library(pubsub_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/pubsub"
    PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/pubsub/v1beta2/pubsub.proto"
    )
googleapis_grpc_proto_library(spanner_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/spanner"
    )
googleapis_grpc_proto_library(api_client_protos 
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api" 
    PROTOS 
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/error_reason.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/serviceusage/v1beta1/resources.proto"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/serviceusage/v1beta1/serviceusage.proto"
    )

# Libraries that are provided, but not consumed by the project. These are libraries
# containing just one proto! IMHO, I would have combined them all together and leave
# some work to the linker...
googleapis_grpc_proto_library(cloud_speech_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/speech/v1"
    )
googleapis_grpc_proto_library(cloud_texttospeech_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/texttospeech/v1"
    )
googleapis_grpc_proto_library(storage_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/storage/v2"
    )
googleapis_grpc_proto_library(api_http_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/http.proto"
    )
googleapis_grpc_proto_library(api_annotations_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/annotations.proto"
    )
googleapis_grpc_proto_library(api_auth_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/auth.proto"
    )
googleapis_grpc_proto_library(api_distribution_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/distribution.proto"
    )
googleapis_grpc_proto_library(api_field_behavior_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/field_behavior.proto"
    )
googleapis_grpc_proto_library(api_label_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/label.proto"
    )
googleapis_grpc_proto_library(api_launch_stage_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/launch_stage.proto"
    )
googleapis_grpc_proto_library(api_metric_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/metric.proto"
    )
googleapis_grpc_proto_library(api_monitored_resource_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/monitored_resource.proto"
    )
googleapis_grpc_proto_library(api_resource_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/api/resource.proto"
    )
googleapis_grpc_proto_library(devtools_cloudtrace_v2_trace_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/devtools/cloudtrace/v2/trace.proto"
    )
googleapis_grpc_proto_library(devtools_cloudtrace_v2_tracing_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/devtools/cloudtrace/v2/tracing.proto"
    )
googleapis_grpc_proto_library(logging_type_type_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/logging/type"
    )
googleapis_grpc_proto_library(monitoring_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/monitoring/dashboard/v1"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/monitoring/metricsscope/v1"
        "${CONAN_GOOGLEAPIS_PROTOS}/google/monitoring/v3"
    )
googleapis_grpc_proto_library(iam_v1_options_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/v1/options.proto"
    )
googleapis_grpc_proto_library(iam_v1_iam_policy_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/iam/v1/iam_policy.proto"
    )
googleapis_grpc_proto_library(type_calendar_period_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/calendar_period.proto"
    )
googleapis_grpc_proto_library(type_color_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/color.proto"
    )
googleapis_grpc_proto_library(type_date_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/date.proto"
    )
googleapis_grpc_proto_library(type_datetime_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/datetime.proto"
    )
googleapis_grpc_proto_library(type_dayofweek_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/dayofweek.proto"
    )
googleapis_grpc_proto_library(type_expr_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/expr.proto"
    )
googleapis_grpc_proto_library(type_fraction_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/fraction.proto"
    )
googleapis_grpc_proto_library(type_interval_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/interval.proto"
    )
googleapis_grpc_proto_library(type_latlng_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/latlng.proto"
    )
googleapis_grpc_proto_library(type_localized_text_protos
    PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/localized_text.proto"
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/localized_text.proto"
    )
googleapis_grpc_proto_library(type_money_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/money.proto"
    )
googleapis_grpc_proto_library(type_month_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/month.proto"
    )
googleapis_grpc_proto_library(type_phone_number_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/phone_number.proto"
    )
googleapis_grpc_proto_library(type_postal_address_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/postal_address.proto"
    )
googleapis_grpc_proto_library(type_quaternion_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/quaternion.proto"
    )
googleapis_grpc_proto_library(type_timeofday_protos
    GRPC_PROTOS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/type/timeofday.proto"
    )
googleapis_grpc_proto_library(cloud_dialogflow_v2_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/dialogflow/v2"
    )
googleapis_grpc_proto_library(cloud_dialogflow_v2beta1_protos
    GRPC_PROTOS_DIRS
        "${CONAN_GOOGLEAPIS_PROTOS}/google/cloud/dialogflow/v2beta1"
    )


install(
    TARGETS ${GOOGLEAPIS_GRPC_PROTOS_TARGETS}
    EXPORT googleapis-targets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
            COMPONENT google_cloud_cpp_runtime
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_runtime
            NAMELINK_SKIP
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_development)
# With CMake-3.12 and higher we could avoid this separate command (and the
# duplication).
install(
    TARGETS ${GOOGLEAPIS_GRPC_PROTOS_TARGETS}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_development
            NAMELINK_ONLY
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT google_cloud_cpp_development)

install(
    EXPORT googleapis-targets
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/google_cloud_cpp_googleapis"
    COMPONENT google_cloud_cpp_development)


foreach (target ${GOOGLEAPIS_GRPC_PROTOS_TARGETS})
    google_cloud_cpp_install_proto_library_headers("${target}")
    google_cloud_cpp_install_proto_library_protos("${target}" "${CONAN_GOOGLEAPIS_PROTOS}")
endforeach ()
