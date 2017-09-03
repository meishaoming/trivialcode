
CFLAGS = -Wall -I/usr/local/Cellar/openssl/1.0.2j/include
LDFLAGS = -L/usr/local/Cellar/openssl/1.0.2j/lib -lcrypto

all:
	@gcc $(CFLAGS) main.c $(LDFLAGS) -o gen_passwd

clean:
	@$(RM) gen_passwd


