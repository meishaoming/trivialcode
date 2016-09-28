//
// Created by Sam Mei on 2016/9/27.
//

#include <stdio.h>
#include <memory.h>
#include <errno.h>
#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <assert.h>

#include "stun_msg.h"

static void stun_msg_init(struct stun_msg_hdr *hdr) {
  hdr->type = MSG_TYPE_REQUEST_BINDING;
  hdr->cookie = MAGIC_COOKIE;
}

static int stun_msg_add_attr(uint8_t *pattr) {
  return 0; /* return attr length */
}

static void stun_parse_msg(uint8_t *msg, size_t len) {
}

int stun_lookup(const char *nodename, const char *servname) {

  struct addrinfo hints, *res, *res0;

  memset(&hints, 0, sizeof(hints));
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_DGRAM;

  printf("%s:%s\n", nodename, servname);
  int error = getaddrinfo(nodename, servname, &hints, &res);
  if (error) {
    printf("getaddrinfo failed: %s\n", gai_strerror(error));
    return error;
  }

  for (res0 = res; res0; res0 = res0->ai_next) {
    struct sockaddr_in *sin = (void *)res0->ai_addr;
    printf("%s:%d\n", inet_ntoa(sin->sin_addr), ntohs(sin->sin_port));
  }

  int sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
  if (sockfd < 0) {
    freeaddrinfo(res);
    return -1;
  }

  bind(sockfd, res->ai_addr, res->ai_addrlen);

  uint8_t buf[260];
  size_t length = sizeof(struct stun_msg_hdr);
  struct stun_msg_hdr *hdr = (void *) buf;

  memset(buf, 0, sizeof(buf));
  hdr->type = htons(MSG_TYPE_REQUEST_BINDING);
  hdr->len = htons(0);
  hdr->cookie = htonl(MAGIC_COOKIE);
  for (int i = 0; i < sizeof(hdr->tx_id); i++) {
    hdr->tx_id[i] = random();
  }

  error = sendto(sockfd, buf, length, 0, res->ai_addr, res->ai_addrlen);
  if (error < 0) {
    printf("sendto failed: %s\n", strerror(errno));
    close(sockfd);
    goto out;
  }

  struct sockaddr addr;
  socklen_t len;
  ssize_t bytes = (int) recvfrom(sockfd, buf, sizeof(buf), 0, &addr, &len);
  if (bytes < 0) {
    printf("recvfrom failed: %s\n", strerror(errno));
    goto out;
  }
  printf("recv %zd bytes\n", bytes);
  stun_parse_msg(buf, bytes);

  out:
  close(sockfd);
  freeaddrinfo(res);
  return error;
}
