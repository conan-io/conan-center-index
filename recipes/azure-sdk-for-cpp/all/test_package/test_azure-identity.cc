#include <azure/identity/client_certificate_credential.hpp>

#include <exception>

int main()
{
  // Load a missing certificate so that the certificate code, which needs
  // bcrypt and crypt32 on Windows (OpenSSL elsewhere), is linked; it must throw.
  try
  {
    Azure::Identity::ClientCertificateCredential credential("tenant", "client", "missing.pem");
  }
  catch (const std::exception&)
  {
    return 0;
  }

  return 1;
}
