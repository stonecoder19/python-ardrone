from ardrone import libardrone

drone = libardrone.ARDrone()

while True:
	print(drone.navdata.get(0))