import math
import time
import krpc

from screen import Screen

turn_start_altitude = 250
turn_end_altitude = 70000
target_altitude = 100000

conn = krpc.connect(name='Launch into orbit')

while 1:
    try:
        vessel = conn.space_center.active_vessel
        break
    except:
        print("aguardando lançamento...")
        time.sleep(1)

srf_frame = vessel.orbit.body.reference_frame

# Pre-launch setup
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
dynamic_pressure = conn.add_stream(getattr, vessel.flight(srf_frame), 'dynamic_pressure')
stage_1_resources = vessel.resources_in_decouple_stage(stage=1, cumulative=False)
srb_fuel = conn.add_stream(stage_1_resources.amount, 'SolidFuel')

screen = Screen(conn)
screen.add_button("Launch", True, [150, 40], [165, -120])
screen.add_status_of_launch("status")

screen.add_telemetry("speed", "m/s", srf_speed)
screen.add_telemetry("altitude", "m", altitude)
screen.add_telemetry("apoapsis", "m", apoapsis)
screen.add_telemetry("dy pressure", "psi", dynamic_pressure)

screen.update_value_of_element("status", "Ready to launch")

while not screen.get_state_of_button("Launch"):
    time.sleep(.1)

for i in range(3, 0, -1):
    screen.update_value_of_element("status", "counter %d" % i)
    time.sleep(1)

screen.update_value_of_element("status", "Launch!")

# Activate the first stage
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

# Main ascent loop
srbs_separated = False
turn_angle = 0

while True:

    if dynamic_pressure()/10000 > 1:
        x = 0.5 - (dynamic_pressure()/10000)/5
        vessel.control.throttle = x
    elif dynamic_pressure()/10000 < 0.8:
        vessel.control.throttle = 1
    else:
        x=float((1-dynamic_pressure()/10000)+0.8)
        vessel.control.throttle = x

    # Gravity turn
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)

    # Separate SRBs when finished
    if not srbs_separated:
        if srb_fuel() < 0.1:
            vessel.control.activate_next_stage()
            srbs_separated = True
            screen.update_value_of_element("status", 'SRBs separated')

    # Decrease throttle when approaching target apoapsis
    if apoapsis() > target_altitude*0.9:
        screen.update_value_of_element("status", 'Approaching target apoapsis')
        break

    screen.update_telemetry()
    time.sleep(0.1)

# Disable engines when target apoapsis is reached
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    screen.update_telemetry()
screen.update_value_of_element("status", 'Target apoapsis reached')
vessel.control.throttle = 0.0

# Wait until out of atmosphere
screen.update_value_of_element("status", 'Coasting out of atmosphere')
while altitude() < 70500:
    screen.update_telemetry()
    time.sleep(0.1)

# Plan circularization burn (using vis-viva equation)
screen.update_value_of_element("status", 'Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Orientate ship
screen.update_value_of_element("status", 'Orientating ship')
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Wait until burn
screen.update_value_of_element("status", 'Waiting until burn')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)

# Execute burn
screen.update_value_of_element("status", 'Ready to execute burn')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time/2.) > 0:
    screen.update_telemetry()
    time.sleep(0.1)
screen.update_value_of_element("status", 'Executing burn')
vessel.control.throttle = 1.0
time.sleep(burn_time - 0.1)
screen.update_value_of_element("status", 'Fine tuning')
vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
while remaining_burn()[1] > 1:
    screen.update_telemetry()
    time.sleep(0.1)
vessel.control.throttle = 0.0
node.remove()

screen.update_value_of_element("status", 'Launch complete')
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.control.sas = True
time.sleep(1)