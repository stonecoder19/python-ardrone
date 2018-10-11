from ardrone import libardrone
import math

current_location =  [0.0, 0.0]

pid_c_roll = [0.0, 0.0, 0.0] #kp kd ki
pid_c_pitch = [0.0, 0.0,  0.0]

waypoints = [[0.0, 0.0], [0.0, 0.0]]

MAX_SPEED = 0.5

drone = libardrone.ARDrone()

def get_gps_coords():
	pass

def get_heading():
	pass

class PID:

	def ___init__(self, kp, kd, ki):
		self.kp = kp
		self.kd = kd
		self.ki = ki

	def update(error, dt):
		P = error * kp

		D = ((self.prevError - error) / dt) * kd

		I = (self.I += error * dt) * ki

		return P + D + I


def get_distance_and_bearing(start_lat, start_lng, dest_lat, dest_lng):
	R = 6371e3

	lat1_rad = math.radians(start_lat)
	lat2_rad = math.radians(dest_lat)
	delta_lat_rad = math.radians(start_lat - dest_lat)
	delta_lon_rad = math.radians(start_lng - dest_lng)

	a = (math.sin(delta_lat_rad / 2) * math.sin(delta_lat_rad / 2)
		  + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon_rad / 2)
		  * math.sin(delta_lon_rad / 2) * math.sin(delta_lon_rad / 2))

	c = 2 * math.atan(math.sqrt(a) / math.sqrt(1 - a))

	distance = R * c

	a1 = start_lat * 3.14 / 180
	b = start_lng * 3.14  / 180
	c1 = dest_lat * 3.14 / 180
	d =  dest_lng * 3.14 / 180

	if(math.cos(c1) * math.sin(d - b) == 0):
		if(c1 > a1):
			bearing = 0
		else:
			bearing = 180
	else:
		angle = math.atan((math.cos(c1) * math.sin(d - b)) 
					/ (math.sin(c1) * math.cos(a1) - math.sin(a1) * math.cos(c1) * math.cos(d - b)))
		bearing = int(angle * 180 / 3.14 + 360) % 360
	return distance, bearing

def get_distance_vec(start_lat, start_lng, dest_lat, dest_lng):

	distance_x, bearing_x = get_distance_and_bearing(dest_lat, start_lng, 
										dest_lat, dest_lng)
	distance_x = bearing_x < 180 ? distance_x : -distance_x

	distance_y, bearing_y = get_distance_and_bearing(start_lat, dest_lng, 
										dest_lat, dest_lng)
	distance_y = bearing_y < 90 ? distance_y : -distance_y

	distance_r, _ = get_distance_and_bearing(start_lat, start_lng, 
		dest_lat, dest_lng)

	return distance_x, distance_y, distance_r


def limit(n, min_n, max_n):
	if n <= min_n:
		return min_n
	elif n >= max_n:
		return max_n
	else:
		return n


def land_sequence():


def main():
	rollPID = PID(pid_c_roll[0], pid_c_roll[1], pid_c_roll[2])
	pitchPID = PID(pid_c_pitch[0], pid_c_pitch[1], pid_c_pitch[2])
	current_waypoint = 0
	# drone.takeoff()
	while (mission_running):
		dest = waypoints[current_waypoint]

		distance_x, distance_y, distance_r = get_distance_vec(current_location[0], 
										current_location[1], dest[0], dest[1])

		x_error = rollPID.update(distance_x)
		y_error = pitchPID.update(distance_y)

		speed_x = limit(x_error, -MAX_SPEED, MAX_SPEED)
		speed_y = limit(y_error, -MAX_SPEED, MAX_SPEED)

		if(speed_x < 0):
			drone.move_right(abs(speed_x))
		else:
			drone.move_left(speed_x)

		if (speed_y < 0):
			drone.move_forward(abs(speed_y))
		else:
			drone.move_backward(speed_y)

		if(distance_r < 5):
			current_waypoint+=1
			if(current_waypoint == len(waypoints)):
				mission_running = False
				landing = True
				land_time = time.time()
	if(landing):
		while(time.time() - land_time < 5):
			drone.hover()
		drone.land()
		drone.halt()
		landing = False







