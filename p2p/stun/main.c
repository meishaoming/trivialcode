
#include <stdint.h>
#include <assert.h>

int stun_lookup(const char *nodename, const char *servname);

int main(int argc, char *argv[]) {
  assert(argc == 3);
  stun_lookup(argv[1], argv[2]);
  return 0;
}