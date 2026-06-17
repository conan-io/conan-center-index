cmake_minimum_required(VERSION 3.15)
project(test_package C)

if (NOT DEFINED ENV{SUPPORT_PATH})
    message(FATAL_ERROR "SUPPORT_PATH environment variable not defined")
endif()

set(STANDARD_ASN1_FILES
 BIT_STRING.c
 BIT_STRING_oer.c
 INTEGER.c
 INTEGER_oer.c
 NativeInteger.c
 NativeInteger_oer.c
 OBJECT_IDENTIFIER.c
 OCTET_STRING.c
 OCTET_STRING_oer.c
 OPEN_TYPE.c
 OPEN_TYPE_oer.c
 asn_SEQUENCE_OF.c
 asn_SET_OF.c
 asn_application.c
 asn_bit_data.c
 asn_codecs_prim.c
 asn_internal.c
 asn_random_fill.c
 ber_decoder.c
 ber_tlv_length.c
 ber_tlv_tag.c
 constr_CHOICE.c
 constr_CHOICE_oer.c
 constr_SEQUENCE.c
 constr_SEQUENCE_oer.c
 constr_SEQUENCE_OF.c
 constr_SET_OF.c
 constr_SET_OF_oer.c
 constr_TYPE.c
 constraints.c
 der_encoder.c
 oer_decoder.c
 oer_encoder.c
 oer_support.c
 per_decoder.c
 per_encoder.c
 per_opentype.c
 per_support.c
 xer_decoder.c
 xer_encoder.c
 xer_support.c
)

set(GENERATED_FILES
  MyTypes.c
  MyInt.c
)

add_custom_command(
  OUTPUT ${GENERATED_FILES} ${STANDARD_ASN1_FILES}
  COMMAND asn1c -S "$ENV{SUPPORT_PATH}" MyModule.asn1
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS MyModule.asn1
)

add_executable(${PROJECT_NAME} test_package.c ${GENERATED_FILES} ${STANDARD_ASN1_FILES})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
