import pigpio
import time

class X:

   GAP=100
   WAVES=3

   def __init__(self, pi, gpio, channels=8, frame_ms=27):
      self.pi = pi
      self.gpio = gpio

      if frame_ms < 5:
         frame_ms = 5
         channels = 2
      elif frame_ms > 100:
         frame_ms = 100

      self.frame_ms = frame_ms

      self._frame_us = int(frame_ms * 1000)
      self._frame_secs = frame_ms / 1000.0

      if channels < 1:
         channels = 1
      elif channels > (frame_ms // 2):
         channels = int(frame_ms // 2)

      self.channels = channels

      self._widths = [1000] * channels # set each channel to minimum pulse width

      self._wid = [None]*self.WAVES
      self._next_wid = 0

      pi.write(gpio, pigpio.LOW)

      self._update_time = time.time()

   def _update(self):
      wf =[]
      micros = 0
      for i in self._widths:
         wf.append(pigpio.pulse(0, 1<<self.gpio, self.GAP))
         wf.append(pigpio.pulse(1<<self.gpio, 0, i))
         micros += (i+self.GAP)
      # off for the remaining frame period
      wf.append(pigpio.pulse(0, 1<<self.gpio, self._frame_us-micros))

      self.pi.wave_add_generic(wf)
      wid = self.pi.wave_create()
      self.pi.wave_send_using_mode(wid, pigpio.WAVE_MODE_REPEAT_SYNC)
      self._wid[self._next_wid] = wid

      self._next_wid += 1
      if self._next_wid >= self.WAVES:
         self._next_wid = 0

      
      remaining = self._update_time + self._frame_secs - time.time()
      if remaining > 0:
         time.sleep(remaining)
      self._update_time = time.time()

      wid = self._wid[self._next_wid]
      if wid is not None:
         self.pi.wave_delete(wid)
         self._wid[self._next_wid] = None

   def update_channel(self, channel, width):
      self._widths[channel] = width
      self._update()

   def update_channels(self, widths):
      self._widths[0:len(widths)] = widths[0:self.channels]
      self._update()

   def cancel(self):
      self.pi.wave_tx_stop()
      for i in self._wid:
         if i is not None:
            self.pi.wave_delete(i)

if __name__ == "__main__":

    import pandas as pd
    import time
    import PPM
    import pigpio
    
    df = pd.read_excel('dataset/dummy.xlsx')

    print(df)
    
    pi = pigpio.pi()
    
    pi.wave_tx_stop() # start with a clean start
    
    ppm = PPM.X(pi, 6, frame_ms=20)
    
    updates = 0
    
    for pw in range(450, 600, 20):
        for chan in range(8):
            ppm.update_channel(chan,pw)
            updates += 1
        time.sleep(2)
    
    for i in range (len(df)):
        pwm_lst = df.iloc[i,1:7].tolist()
        final_lst = list(map(int, pwm_lst))
        print(final_lst)
        ppm.update_channels(final_lst)
        updates += 1
        time.sleep(0.1)
    
    ppm.update_channels([100,110,120,130,140,150,100,500])
    
    time.sleep(2)
    
    ppm.cancel()
    
    pi.stop()
    