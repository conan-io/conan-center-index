
#include "nanotdf_client.h"

using namespace virtru;

const char *sender_private_key = "-----BEGIN PRIVATE KEY-----\n" \
"MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgi/Qr/jF1vkvCtVRn\n" \
"JH25ie37emp8icaowPqgIkFvQgihRANCAARlujKGIcl2ibpir9JKycCnjLZG5Ald\n" \
"6G4o6B340ejGV2XWyyARligEcCCXXeHDe/cfBQm/ODavaNUuZoxp130L\n" \
"-----END PRIVATE KEY-----";

const char *recipient_public_key = "-----BEGIN PUBLIC KEY-----\n" \
"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE2SU1P4ECFK4V3/Yxx29qgwqbiC9z\n" \
"K4pt21P3DnZBJufh62/bNYhQkL3VQ9oM13FvcKpbIf6Hi83ry0O2vmE5mQ==\n" \
"-----END PUBLIC KEY-----";

int main(int argc, char **argv) {

  NanoTDFClient nano_tdf_client("https://your-eas-url.here", "your@user.here");

  nano_tdf_client.setDecrypterPublicKey(recipient_public_key);

  nano_tdf_client.setSignerPrivateKey(sender_private_key, EllipticCurve::SECP256R1);

  return 0;
}
