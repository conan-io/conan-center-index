#include <cstddef>
#include <kalshi/kalshi.hpp>
#include <memory>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <string>
#include <string_view>

class Fixture final : public kalshi::HttpTransport {
public:
  kalshi::Result<kalshi::HttpResponse>
  request(kalshi::HttpMethod, std::string_view,
          std::string_view) const override {
    return kalshi::HttpResponse{
        200, R"({"exchange_active":true,"trading_active":false})", {}};
  }
};
int main() {
  kalshi::KalshiClient client(std::make_shared<Fixture>());
  const kalshi::Result<kalshi::ExchangeStatus> status =
      client.get_exchange_status();
  if (!status || !status->exchange_active || status->trading_active) {
    return 1;
  }
  const std::unique_ptr<EVP_PKEY, decltype(&EVP_PKEY_free)> key(
      EVP_PKEY_Q_keygen(nullptr, nullptr, "ED25519"), &EVP_PKEY_free);
  const std::unique_ptr<BIO, decltype(&BIO_free)> output(BIO_new(BIO_s_mem()),
                                                         &BIO_free);
  if (!key || !output) {
    return 2;
  }
  const int encoded = PEM_write_bio_PrivateKey(output.get(), key.get(), nullptr,
                                               nullptr, 0, nullptr, nullptr);
  char *data = nullptr;
  const long length = BIO_get_mem_data(output.get(), &data);
  if (encoded != 1 || length <= 0) {
    return 3;
  }
  const kalshi::Result<kalshi::Signer> signer = kalshi::Signer::from_pem(
      "fixture-key", std::string_view(data, static_cast<std::size_t>(length)));
  if (!signer || !signer->sign("GET", "/trade-api/ws/v2")) {
    return 4;
  }
  const kalshi::WebSocketClient ws(*signer);
  return ws.is_connected() ? 5 : 0;
}
