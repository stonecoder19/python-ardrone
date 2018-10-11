import socket
import threading

ARDRONE_COMMAND_PORT = 5556

class AT:

	def __init__(self,ip,lock,com_watchdog_timer):
		self.ip = ip
		self.seq = 1
		self.lock = lock
		self.timer_t = 0.2
		self.com_watchdog_timer = com_watchdog_timer

	def send_cmd(self,command, params):
		self.lock.acquire()
		self.com_watchdog_timer.cancel()
		param_str = ''
		for p in params:
			if type(p) == int:
				param_str += ",%d" % p
			elif type(p) == float:
				param_str += ",%d" % f2i(p)
			elif type(p) == str:
				param_str += ',"'+p+'"'
		msg = "AT*%s=%i%s\r" % (command, self.seq, param_str)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(msg, (self.ip, ARDRONE_COMMAND_PORT))
		self.seq += 1
		self.com_watchdog_timer = threading.Timer(self.timer_t, self.comwdg)
		self.com_watchdog_timer.start()
		self.lock.release()

    ###############################################################################
    ### Low level AT Commands
    ###############################################################################

    
	def at_config(self,option, value):
		"""Set configuration parameters of the drone."""
		self.send_cmd('CONFIG', [str(option), str(value)])

	def comwdg(self):
		"""
		Reset communication watchdog.
		"""
		# FIXME: no sequence number
		self.send_cmd('COMWDG',[])

	def at_ftrim(self):
		"""
		Tell the drone it's lying horizontally.

		Parameters:
		seq -- sequence number
		"""
		self.send_cmd('FTRIM',[])

	
	def at_ref(self,takeoff, emergency=False):
	    """
	    Basic behaviour of the drone: take-off/landing, emergency stop/reset)

	    Parameters:
	    seq -- sequence number
	    takeoff -- True: Takeoff / False: Land
	    emergency -- True: Turn of the engines
	    """
	    p = 0b10001010101000000000000000000
	    if takeoff:
	        p += 0b1000000000
	    if emergency:
	        p += 0b0100000000
	    self.send_cmd('REF', [p])
    

	def at_pcmd(self, progressive, lr, fb, vv, va):
		"""
		Makes the drone move (translate/rotate).

		Parameters:
		seq -- sequence number
		progressive -- True: enable progressive commands, False: disable (i.e.
		    enable hovering mode)
		lr -- left-right tilt: float [-1..1] negative: left, positive: right
		rb -- front-back tilt: float [-1..1] negative: forwards, positive:
		    backwards
		vv -- vertical speed: float [-1..1] negative: go down, positive: rise
		va -- angular speed: float [-1..1] negative: spin left, positive: spin 
		    right

		The above float values are a percentage of the maximum speed.
		"""
		p = 1 if progressive else 0
		self.send_cmd('PCMD', [p, float(lr), float(fb), float(vv), float(va)])

	def at_zap(self, stream):
	    """
	    Selects which video stream to send on the video UDP port.

	    Parameters:
	    seq -- sequence number
	    stream -- Integer: video stream to broadcast
	    """
	    # FIXME: improve parameters to select the modes directly
	    self.send_cmd('ZAP', [stream])

	def at_aflight(self, flag):
		"""
		Makes the drone fly autonomously.

		Parameters:
		seq -- sequence number
		flag -- Integer: 1: start flight, 0: stop flight
		"""
		self.send_cmd('AFLIGHT', [flag])

	def at_pwm(self, m1, m2, m3, m4):
		"""
		Sends control values directly to the engines, overriding control loops.

		Parameters:
		seq -- sequence number
		m1 -- front left command
		m2 -- fright right command
		m3 -- back right command
		m4 -- back left command
		"""
		# FIXME: what type do mx have?
		self.send_cmd('PWM', [m1, m2, m3, m4])

	def at_led(self, anim, f, d):
		"""
		Control the drones LED.

		Parameters:
		seq -- sequence number
		anim -- Integer: animation to play
		f -- ?: frequence in HZ of the animation
		d -- Integer: total duration in seconds of the animation
		"""
		self.send_cmd('LED', [anim, float(f), d])

	def at_anim(self, anim, d):
		"""
		Makes the drone execute a predefined movement (animation).

		Parameters:
		seq -- sequcence number
		anim -- Integer: animation to play
		d -- Integer: total duration in sections of the animation
		"""
		self.send_cmd('ANIM', [anim, d])


