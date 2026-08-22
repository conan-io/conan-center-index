// from: https://github.com/cisco/libsrtp#example-code

#include <srtp2/srtp.h>

#include <string.h>

int main(void)
{
	srtp_t session;
	srtp_policy_t policy;

	// Set key to predetermined value
	uint8_t key[30] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
					   0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
					   0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
					   0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D};

	// initialize libSRTP
	srtp_init();

	// default policy values
	memset(&policy, 0x0, sizeof(srtp_policy_t));

	// set policy to describe a policy for an SRTP stream
	srtp_crypto_policy_set_rtp_default(&policy.rtp);
	srtp_crypto_policy_set_rtcp_default(&policy.rtcp);
	policy.key = key;

	// allocate and initialize the SRTP session
	srtp_create(&session, &policy);

	return 0;
}
