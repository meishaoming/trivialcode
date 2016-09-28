//
// Created by Sam Mei on 2016/9/27.
//

#ifndef STUN_STUN_MSG_H
#define STUN_STUN_MSG_H

#include <stdint.h>

/*
 * Format of STUN Message Header
 *
 *  0               1               2               3
 *  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |0 0|    STUN Message Type      |      Message  Length          |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |                        Magic Cookie                           |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |                                                               |
 * |                  Transaction ID (96 bits)                     |
 * |                                                               |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *
 *  0                 1
 *  2  3  4 5 6 7 8 9 0 1 2 3 4 5
 * +--+--+-+-+-+-+-+-+-+-+-+-+-+-+
 * |M |M |M|M|M|C|M|M|M|C|M|M|M|M|
 * |11|10|9|8|7|1|6|5|4|0|3|2|1|0|
 * +--+--+-+-+-+-+-+-+-+-+-+-+-+-+
 *
 * message class
 * C1C0 :
 *   0b00 request
 *   0b01 indication
 *   0b10 success response
 *   0b11 error response
 *
 * STUN method
 * M11..M0 :
 *   0x000 Reserved
 *   0x001 Binding
 *   0x002 Reversed; was SharedSecret
 */

struct stun_msg_hdr {
  uint16_t type;
  uint16_t len;
  uint32_t cookie;
  uint8_t tx_id[12];
};

#define MAGIC_COOKIE 0x2112A442

#define MSG_TYPE_REQUEST_BINDING  0x0001
#define MSG_TYPE_RESPONSE_SUCCESS 0x0101
#define MSG_TYPE_RESPONSE_ERROR   0x0101

enum stun_msg_class_e {
  STUN_MSG_CLASS_REQUEST,
  STUN_MSG_CLASS_RESPONSE,
};

/*
 * STUN attribute
 *
 *  0               1               2               3
 *  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |             Type              |             Length            |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |                        Value (variable) ....
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *
 * Each STUN attribute MUST end on a 32-bit boundary.
 */
struct stun_attr {
  uint16_t type;
  uint16_t length;
  uint8_t value[];
};

enum stun_attr_type_e {

  /* Comprehension-required range (0x0000-0x7FFF): */

  STUN_ATTR_TYPE_RESERVED           = 0x0000, // (Reserved)
  STUN_ATTR_TYPE_MAPPED_ADDRESS     = 0x0001, // MAPPED-ADDRESS
  STUN_ATTR_TYPE_RESPONSE_ADDRESS   = 0x0002, // (Reserved; was RESPONSE-ADDRESS)
  STUN_ATTR_TYPE_CHANGE_ADDRESS     = 0x0003, // (Reserved; was CHANGE-ADDRESS)
  STUN_ATTR_TYPE_SOURCE_ADDRESS     = 0x0004, // (Reserved; was SOURCE-ADDRESS)
  STUN_ATTR_TYPE_CHANGED_ADDRESS    = 0x0005, // (Reserved; was CHANGED-ADDRESS)
  STUN_ATTR_TYPE_USERNAME           = 0x0006, // USERNAME
  STUN_ATTR_TYPE_PASSWORD           = 0x0007, // (Reserved; was PASSWORD)
  STUN_ATTR_TYPE_MESSAGE_INTEGRITY  = 0x0008, // MESSAGE-INTEGRITY
  STUN_ATTR_TYPE_ERROR_CODE         = 0x0009, // ERROR-CODE
  STUN_ATTR_TYPE_UNKNOWN_ATTRIBUTES = 0x000A, // UNKNOWN-ATTRIBUTES
  STUN_ATTR_TYPE_REFLECTED_FROM     = 0x000B, // (Reserved; was REFLECTED-FROM)
  STUN_ATTR_TYPE_REALM              = 0x0014, // REALM
  STUN_ATTR_TYPE_NONCE              = 0x0015, // NONCE
  STUN_ATTR_TYPE_XOR_MAPPED_ADDRESS = 0x0020, // XOR-MAPPED-ADDRESS

  /* Comprehension-optional range (0x8000-0xFFFF) */

  STUN_ATTR_TYPE_SOFTWARE           = 0x8022, // SOFTWARE
  STUN_ATTR_TYPE_ALTERNATE_SERVER   = 0x8023, // ALTERNATE-SERVER
  STUN_ATTR_TYPE_FINGERPRINT        = 0x8028, // FINGERPRINT
};

/*
 * Format of MAPPED-ADDRESS Attribute
 *
 *  0               1               2               3
 *  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |0 0 0 0 0 0 0 0|    Family     |             Port              |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |                                                               |
 * |               Address (32 bits or 128 bits)                   |
 * |                                                               |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

struct stun_attr_maddped_addr {
  uint8_t reversed;
  uint8_t family;
  uint16_t port;
  uint32_t addr;
};

/*
 * Format of XOR-MAPPED-ADDRESS Attribute
 *
 *  0               1               2               3
 *  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |0 0 0 0 0 0 0 0|    Family     |           X-Port              |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |                                                               |
 * |             X-Address (32 bits or 128 bits)                   |
 * |                                                               |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

/*
 * ERROR-CODE Attribute
 *
 *  0               1               2               3
 *  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |    Reserved, should be 0                |Class|   Number      |
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 * |       Reason Phrase (variable)                               ..
 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */

enum stun_attr_errorcode_t {
  STUN_ERRORCODE_TRY_ALTERNATE     = 300,
  STUN_ERRORCODE_BAD_REQUEST       = 400,
  STUN_ERRORCODE_UNAUTHORIZED      = 401,
  STUN_ERRORCODE_UNKNOWN_ATTRIBUTE = 420,
  STUN_ERRORCODE_STALE_NONCE       = 438,
  STUN_ERRORCODE_SERVER_ERROR      = 500,
};

#endif //STUN_STUN_MSG_H
