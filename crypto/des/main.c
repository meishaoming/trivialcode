#include <stdint.h>
#include <printf.h>
#include "des.h"

static uint8_t key[] = "3a2fb9c9";
static uint8_t in_buf[] = "12345678";
static uint8_t out_buf[] = "12345678";

int main(void)
{
  des_context des_ctx;
  des_ctx.mode = DES_ENCRYPT;

  des_setkey_enc(&des_ctx, key);
  des_crypt_ecb(&des_ctx, in_buf, out_buf);

  for (int i = 0; i < 8; i++) {
    printf("%02x", out_buf[i]);
  }
  printf("\n");

  des_ctx.mode = DES_DECRYPT;
  des_setkey_dec(&des_ctx, key);
  des_crypt_ecb(&des_ctx, out_buf, out_buf);
  printf("%s\n", out_buf);

  return 0;
}
