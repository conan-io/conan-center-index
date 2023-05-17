/**
 * @file test_package.cpp
 * @author ofir iluz (iluzofir@gmail.com)
 * @brief
 * @version 0.1
 * @date 2022-08-22
 *
 * @copyright Copyright (c) 2022
 *
 */

#include "octo-keygen-cpp/openssl/ssl-keygen.hpp"
#include "octo-keygen-cpp/openssl/ssl-keypair.hpp"
#include "octo-keygen-cpp/openssl/ssl-keypair-certificate-chain.hpp"
#include "octo-keygen-cpp/openssl/ssl-keypair-certificate.hpp"
#include <octo-logger-cpp/manager.hpp>
#include <iostream>
#include <fstream>


constexpr auto ROOTCA = "-----BEGIN CERTIFICATE-----\n"
                    "MIID4DCCAsigAwIBAgIUSdyfMTrtlHmyB8Jr3/q0YjizVCQwDQYJKoZIhvcNAQEN\n"
                    "BQAwfDELMAkGA1UEBhMCSUwxDzANBgNVBAgMBklzcmFlbDEUMBIGA1UEBwwLUGV0\n"
                    "YWggVGlrdmExETAPBgNVBAoMCEN5YmVyQXJrMREwDwYDVQQLDAhDeWJlckFyazEg\n"
                    "MB4GA1UEAwwXY29tcHV0ZS0xLmFtYXpvbmF3cy5jb20wHhcNMjIwNDI4MTQxMzI0\n"
                    "WhcNMjIwNTI4MTQxMzI0WjB8MQswCQYDVQQGEwJJTDEPMA0GA1UECAwGSXNyYWVs\n"
                    "MRQwEgYDVQQHDAtQZXRhaCBUaWt2YTERMA8GA1UECgwIQ3liZXJBcmsxETAPBgNV\n"
                    "BAsMCEN5YmVyQXJrMSAwHgYDVQQDDBdjb21wdXRlLTEuYW1hem9uYXdzLmNvbTCC\n"
                    "ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJP1+lRasxk7eBieEW+ctdcY\n"
                    "fTTSiiVUfG0aLO1vm4ZuawTaXkQM5NVN/Cp0N2iNcCZqtSza28WqNCfomRrwIhAG\n"
                    "VIlDFr+7O/ajorNA0GyD7+jBrzicNn5dPZMfpRXsNEePhlUYg04e970BIVpLT8dR\n"
                    "t0z0FAeyMu1fR2GCg3y1M2d9aF7AmwZECzjyPCUk7dpHVphK2Hvvrd5+mkmxn7v2\n"
                    "8N2p4+gSG6+khKUW+E4X/zWxjBDnn3EdVFwn7d6BHw2z7Xdw4wkk5RbB0lb0W/DW\n"
                    "8kd0ZVdq6BhwLvOLBGaDhuh+rqIiRI+QNJmCJoKf9uUOZNm9/FajKYv8uF0ZQ90C\n"
                    "AwEAAaNaMFgwDgYDVR0PAQH/BAQDAgKkMA8GA1UdEwEB/wQFMAMBAf8wFgYDVR0l\n"
                    "AQH/BAwwCgYIKwYBBQUHAwEwHQYDVR0OBBYEFH3dUC27VCMzARsItn7XkHE+ITx3\n"
                    "MA0GCSqGSIb3DQEBDQUAA4IBAQAsP4xc0WgKqKM10Ng8bMlLvZ5M7p7aOCIO5U5C\n"
                    "jKLE0sitD86jQzJNfFz2gfVG/L/hRVejMaRtiOoc/CbAEeJk4zGPf+UKNzkzgi53\n"
                    "jWe4qd6FXMERymMDWRDW222TVyqhVE4wRLkkDPZVyK3sq8C70AnsI2S5JCzU9+en\n"
                    "OwnpXXMkP7hRqeLa70FM/yqRZyv4Ys0XvjdMdtRh2zAEOq82rU3cRQA8P4uEzpPh\n"
                    "5ugeJKLdqERLsnOshBr+M2AcmXSx1lY92rX+Bk7LntazHDe6ql0J4HtjY2+DL5od\n"
                    "EB4MfKwH5Hh+LLVDvZablJHTHHhLahp8VT57xaxGUBwpNsnI\n"
                    "-----END CERTIFICATE-----";

constexpr auto SUBCA = "-----BEGIN CERTIFICATE-----\n"
                       "MIIDeTCCAmGgAwIBAgIBADANBgkqhkiG9w0BAQ0FADB8MQswCQYDVQQGEwJJTDEP\n"
                       "MA0GA1UECAwGSXNyYWVsMRQwEgYDVQQHDAtQZXRhaCBUaWt2YTERMA8GA1UECgwI\n"
                       "Q3liZXJBcmsxETAPBgNVBAsMCEN5YmVyQXJrMSAwHgYDVQQDDBdjb21wdXRlLTEu\n"
                       "YW1hem9uYXdzLmNvbTAeFw0yMjA0MjgxNDQ3NDVaFw0yNTAyMTUxNDQ3NDVaMCgx\n"
                       "JjAkBgNVBAMMHWxvY2FsLmNvbXB1dGUtMS5hbWF6b25hd3MuY29tMIIBIjANBgkq\n"
                       "hkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAo8lmtezRqfQGw2HFrY+7CTmq79xVXoMy\n"
                       "0e0rTOI7M4mhGiLOZ47F7ADjvC+So6/2ovTGgLEkPu5VINkpeL2hwGjOb3uLbCZR\n"
                       "VO9tAEJJMkr8bWwajGb2vTVh03YCPZlBxMS118rxqz8dUNgvjTYCSqhRfHy6VTkR\n"
                       "7rKvUm08OplhpDqqOwoIG4wz2eRw9xV4UUBKa8cDOhzEuvQlsqH4BEmV6PO/0BiR\n"
                       "d2g00PgPYjSLe3RMccdy5DtyyRuzQn28ptYi/wQ+nBz00EPfagt+00b9HObtP6VH\n"
                       "rdzVzqYTajeMqfQVGQCSa/+AEhDZZ6BuXGIKvno7ZSlvFJ9BUbE8rQIDAQABo1ow\n"
                       "WDAOBgNVHQ8BAf8EBAMCAqQwDwYDVR0TAQH/BAUwAwEB/zAWBgNVHSUBAf8EDDAK\n"
                       "BggrBgEFBQcDATAdBgNVHQ4EFgQUxvs7lTceDZviJqY18ZstMujWkMIwDQYJKoZI\n"
                       "hvcNAQENBQADggEBADdwVWdETkOjsIhX85ONYvah/BxzHp+Ts7vf+Jniem7WKxkM\n"
                       "bF+dcODbeFYacbyNl6lr7NgarQaDXS9B6BH5MExdsxeWmHOT5sp1RTcWX+mSL5w5\n"
                       "K9rqmvG3WuLLE1qV4GJOr5rpEeW461uIzfPRUNCUx7hcJTeR8uX8jAkmWoh1eqGZ\n"
                       "OYHMzux6604Ph1qG5RSpowetjbeEFljsTAxGl+f5JgrO65WLNcGwiH5bIQ3FEZmD\n"
                       "682u2K0IZOUUEwe64tWZZERXoYFHXvS8UPfcnHsgkO2+ipWBxwGfOaCGmadDzgRR\n"
                       "kkZ9Ftu1SOFJRUopr8uadjayMBHrX4HXS7O8fO4=\n"
                       "-----END CERTIFICATE-----";

constexpr auto TARGET_CERT = "-----BEGIN CERTIFICATE-----\n"
                             "MIIDKTCCAhGgAwIBAgIBADANBgkqhkiG9w0BAQ0FADAoMSYwJAYDVQQDDB1sb2Nh\n"
                             "bC5jb21wdXRlLTEuYW1hem9uYXdzLmNvbTAeFw0yMjA0MjgxNDQ4NDNaFw0yNTAy\n"
                             "MTUxNDQ4NDNaMCsxKTAnBgNVBAMMICouZ2xvYmFsLmNvbXB1dGUtMS5hbWF6b25h\n"
                             "d3MuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA18Ht/JD/rjl8\n"
                             "8XZrQhZXx1RY8R2zDEj95LQAAAt++slmEplCrMubFDRiHUMiRbatq1a0bFUUIFqg\n"
                             "6D7v2olar88sdofnyneDSPnTYv1BIlzblhWTFZ0uSakhOzKgCiVn38iwyChG/HVc\n"
                             "7XNcin1fqfYTLPs6fmPpRTgowAorjvUP8BdkhK+QJ9IiIAB24BMJXn8k/0Z/G4Jr\n"
                             "VsCGysxNJgAzQDZBlXvBVS7aNixuTh1A1bdU7ag+V1oUPXimBVmGLrLv50tls6Ys\n"
                             "kdJ/yc6vsXahTqKTgF8uL+bxaD7CQGhuijAQU1QgvTX/P2D2/9GJ/3dCdRFOMkag\n"
                             "eTSR7ALF4QIDAQABo1swWTAJBgNVHRMEAjAAMAsGA1UdDwQEAwIFoDATBgNVHSUE\n"
                             "DDAKBggrBgEFBQcDATAqBgNVHREEIzAhgh8qLmxvY2FsLmNvbXB1dGUtMS5hbWF6\n"
                             "b25hd3MuY29tMA0GCSqGSIb3DQEBDQUAA4IBAQA5UfViA+Q8Oxk+aNABw5NgERtC\n"
                             "TwZNqwYIKH7NB5whOUwaK7EDemZP56HdbIWxqjuUF4EZ+7glUgFsy8/DNJoZbf48\n"
                             "BIQw0rig8LqRDKJznz5oznUPJtaNKC/nZ1neY0B+ZJNLCRh+GDh4d+4/huRSa9jP\n"
                             "SUsHvLVgsp1enlkTpZ6NjX0oUB2mRpT64ei+kg+R/lnWgWTctyORfUZFLHxhGGYf\n"
                             "RCW+mJQLn+Ashbctb+7fdFuGLj92VaB36zrdmxKAxHMXSbABlVMTY0DzMdvO7VId\n"
                             "LJOZq84H9k4ERbZD/tWZSFd3HqvfV++1o4C+7/GZMV4j1DgWKHMrQv/fvh2X\n"
                             "-----END CERTIFICATE-----";


int main(int argc, char** argv)
{
    octo::logger::Logger logger("PSKeygen");
    std::shared_ptr<octo::logger::ManagerConfig> config =
        std::make_shared<octo::logger::ManagerConfig>();
    octo::logger::SinkConfig console_writer_sink("Console", octo::logger::SinkConfig::SinkType::CONSOLE_SINK);
    config->add_sink(console_writer_sink);
    octo::logger::Manager::instance()
        .editable_channel("PSKeygen")
        .set_log_level(octo::logger::Log::LogLevel::DEBUG);
    octo::logger::Manager::instance().configure(config);

    auto ca = octo::keygen::ssl::SSLKeypairCertificateChain::load_certificate_chain(
        std::make_unique<octo::encryption::SecureString>(ROOTCA)
    );
    auto target = octo::keygen::ssl::SSLKeypairCertificate::load_certificate(
        std::make_unique<octo::encryption::SecureString>(TARGET_CERT)
    );
    auto chain = octo::keygen::ssl::SSLKeypairCertificateChain::load_certificate_chain(
        std::make_unique<octo::encryption::SecureString>(SUBCA)
    );
    logger.info() << "IS CA = " << ca->is_any_ca();
    logger.info() << "IS VALID CERT = " << ca->is_valid_chain(target.get(),
                                                              chain.get());

    octo::keygen::KeygenPtr ssl_key_gen = std::make_shared<octo::keygen::ssl::SSLKeygen>();
    octo::keygen::KeygenOptions ssl_opts;
    octo::keygen::KeypairPtr ssl_key_pair = ssl_key_gen->generate_keypair(ssl_opts);
    logger.info() << "\n" << ssl_key_pair->private_key();
    logger.info() << "\n" << ssl_key_pair->public_key();

    octo::keygen::KeygenOptions ssl_sign_opts;
    octo::keygen::KeypairCertificatePtr ssl_cert = ssl_key_gen->sign_key_pair(ssl_key_pair, ssl_sign_opts);
    logger.info() << "\n" << ssl_cert->certificate();
    logger.info() << "\n" << ssl_cert->pretty_print_certificate_info();
}
