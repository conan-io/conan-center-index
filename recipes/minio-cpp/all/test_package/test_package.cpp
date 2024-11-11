#include <miniocpp/client.h>

int main(int argc, char* argv[]) {
  minio::s3::BaseUrl base_url("example.com");

  minio::creds::StaticProvider provider("access_key", "secret_key");

  minio::s3::Client client(base_url, &provider);
}
