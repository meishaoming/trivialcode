#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>

#define ARRAY_SIZE(a)	(sizeof(a)/sizeof(a[0]))

static uint8_t sha1_result[SHA_DIGEST_LENGTH];
static uint8_t priv_key[] = "5fb04c71686a6fa935135f76e44";
static uint8_t location[] = "d415be835c059f";
static uint32_t passwd_array[10000];

// key + location + timestamp + index

static uint32_t get_timestamp_of_day(void)
{
  time_t timestamp = time(NULL);
  struct tm *ltm = localtime(&timestamp);
  ltm->tm_hour = 0;
  ltm->tm_min = 0;
  ltm->tm_sec = 0;
  timestamp = mktime(ltm);
  return timestamp;
}

static uint32_t generate_number(uint8_t *sha1_array)
{
  uint8_t offset = sha1_array[SHA_DIGEST_LENGTH-1] & 0xf;
  uint32_t number;
  memcpy(&number, &sha1_array[offset], sizeof(number));
  number %= 1000000;
  return number;
}

static void hash(uint8_t *sha1_array, uint32_t index)
{
  uint32_t timestamp = get_timestamp_of_day();
  SHA_CTX ctx;
  SHA1_Init(&ctx);
  SHA1_Update(&ctx, priv_key, sizeof(priv_key) - 1);
  SHA1_Update(&ctx, location, sizeof(location) - 1);
  SHA1_Update(&ctx, &timestamp, sizeof(timestamp));
  SHA1_Update(&ctx, &index, sizeof(index));
  SHA1_Final(sha1_array, &ctx);
}

int main()
{
  for (uint32_t index = 0; index < ARRAY_SIZE(passwd_array); index++) {
    hash(sha1_result, index);
    passwd_array[index] = generate_number(sha1_result);
    for (int i = 0; i < index; i++) {
	    if (passwd_array[index] == passwd_array[i]) {
		    printf("%06d\n", passwd_array[index]);
	    }
    }
  }

  return 0;
}

