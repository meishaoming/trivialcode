/*
 * =====================================================================================
 *
 *       Filename:  test_event.cc
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  10/02/2016 16:48:53
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  YOUR NAME (), 
 *   Organization:  
 *
 * =====================================================================================
 */

#include <iostream>

#include <webrtc/base/event.h>
#include <webrtc/base/platform_thread.h>

bool thread_func(void *obj) {
  rtc::Event *ev = static_cast<rtc::Event *>(obj);

  std::cout << "ev wait start ..." << std::endl;
  ev->Wait(rtc::Event::kForever);
  std::cout << "ev wait stop ..." << std::endl;

  /* Return true make thread loop until thread.Stop().
   * Here return false to exit thread
   */
  std::cout << "thread exit ..." << std::endl;
  return false;
}

int main(void) {
  rtc::Event ev(false, false);

  rtc::PlatformThread thread(thread_func, &ev, "event thread");
  thread.Start();

  getchar();
  ev.Set();

  getchar();
  std::cout << "main thread exit ..." << std::endl;
  return 0;
}
