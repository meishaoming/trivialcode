
static char base64[] =
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

struct b64state {
	u32_t bs_bits;
	int bs_offs;
};

int b64enc(struct b64state *bs, u_char *inp, int inlen, u_char *outp)
{
	int outlen = 0;

	while (inlen > 0) {
		bs->bs_bits = (bs->bs_bits << 8) | *inp++;
		inlen--;
		bs->bs_offs += 8;
		if (bs->bs_offs >= 24) {
			*outp++ = base64[(bs->bs_bits >> 18) & 0x3F];
			*outp++ = base64[(bs->bs_bits >> 12) & 0x3F];
			*outp++ = base64[(bs->bs_bits >> 6) & 0x3F];
			*outp++ = base64[bs->bs_bits & 0x3F];
			outlen += 4;
			bs->bs_offs = 0;
			bs->bs_bits = 0;
		}
	}
	return outlen;
}

int b64flush(struct b64state *bs, u_char *outp)
{
	int outlen = 0;

	if (bs->bs_offs == 8) {
		*outp++ = base64[(bs->bs_bits >> 2) & 0x3F];
		*outp++ = base64[(bs->bs_bits << 4) & 0x3F];
		outlen = 2;
	} else if (bs->bs_offs == 16) {
		*outp++ = base64[(bs->bs_bits >> 10) & 0x3F];
		*outp++ = base64[(bs->bs_bits >> 4) & 0x3F];
		*outp++ = base64[(bs->bs_bits << 2) & 0x3F];
		outlen = 3;
	}
	bs->bs_offs = 0;
	bs->bs_bits = 0;
	return outlen;
}

int b64dec(struct b64state *bs, u_char *inp, int inlen, u_char *outp)
{
	int outlen = 0;
	char *cp;

	while (inlen > 0) {
		if ((cp = strchr(base64, *inp++)) == NULL)
			break;
		bs->bs_bits = (bs->bs_bits << 6) | (cp - base64);
		inlen--;
		bs->bs_offs += 6;
		if (bs->bs_offs >= 8) {
			*outp++ = bs->bs_bits >> (bs->bs_offs - 8);
			outlen++;
			bs->bs_offs -= 8;
		}
	}
	return outlen;
}

