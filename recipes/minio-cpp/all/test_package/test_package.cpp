#include <miniocpp/client.h>

int main(int argc, char* argv[]) {
  minio::s3::BaseUrl base_url("play.min.io");

  minio::creds::StaticProvider provider(
      "Q3AM3UQ867SPQQA43P2F", "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG");

  minio::s3::Client client(base_url, &provider);
}
