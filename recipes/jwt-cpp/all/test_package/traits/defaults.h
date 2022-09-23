#ifndef JWT_CPP_KAZUHO_PICOJSON_DEFAULTS_H
#define JWT_CPP_KAZUHO_PICOJSON_DEFAULTS_H

#include "traits.h"

namespace jwt {
  /**
   * \brief a class to store a generic [picojson](https://github.com/kazuho/picojson) value as claim
   *
   * This type is the specialization of the \ref basic_claim class which
   * uses the standard template types.
   */
  using claim = basic_claim<traits::kazuho_picojson>;

  /**
   * Create a verifier using the default clock
   * \return verifier instance
   */
  inline verifier<default_clock, traits::kazuho_picojson> verify() {
    return verify<default_clock, traits::kazuho_picojson>(default_clock{});
  }

  /**
   * Return a builder instance to create a new token
   */
  inline builder<traits::kazuho_picojson> create() { return builder<traits::kazuho_picojson>(); }

#ifndef JWT_DISABLE_BASE64
  /**
   * Decode a token
   * \param token Token to decode
   * \return Decoded token
   * \throw std::invalid_argument Token is not in correct format
   * \throw std::runtime_error Base64 decoding failed or invalid json
   */
  inline decoded_jwt<traits::kazuho_picojson> decode(const std::string& token) {
    return decoded_jwt<traits::kazuho_picojson>(token);
  }
#endif

  /**
   * Decode a token
   * \tparam Decode is callabled, taking a string_type and returns a string_type.
   * It should ensure the padding of the input and then base64url decode and
   * return the results.
   * \param token Token to decode
   * \param decode The token to parse
   * \return Decoded token
   * \throw std::invalid_argument Token is not in correct format
   * \throw std::runtime_error Base64 decoding failed or invalid json
   */
  template<typename Decode>
  decoded_jwt<traits::kazuho_picojson> decode(const std::string& token, Decode decode) {
    return decoded_jwt<traits::kazuho_picojson>(token, decode);
  }
} // namespace jwt

#endif // JWT_CPP_KAZUHO_PICOJSON_DEFAULTS_H
