https://stackoverflow.com/questions/125099/formula-for-controlling-the-movement-of-a-tank-like-vehicle

*Wc* = speed of imaginary centre wheel
*Wo* = speed of outer track
*Wi* = speed of inner track
*R* = turn radius from the centre of the robot
*d* = distance between tracks

Wo = Wc * ((0.5R+d)/0.5R)
Wi = Wc * ((0.5R-d)/0.5R)

- Box is 0.075m wide 
- Wheel has a radius of 0.02 (*r*) and a height of 0.01
- Hence, *d* = 0.075 + 0.01 = 0.085
- The speed of the wheel is *w* (rad/s)

Assuming no major wheel slippage, the ground speed of a wheel is given by:

s = rw (m/s)

The rotational velocity of the robot can be calculated with a given turning radius and the ground speed of the inner wheel:

a' = (Wc * r)/R

- Robot angle is *a* (hence the rotational velocity is *a'*)

From this, we can use this to create a system to control the differential drive of the robot.

Inputs are Robot speed (from centre of mass), turn speed (around centre of rotation):

- *Sc* = robot speed (m/s)
- *a'* = robot rotation speed (rad/s)

Outputs are the roational speed of the wheels:

- *Wo* = speed of outer wheel (rad/s)
- *Wi* = speed of inner wheel (rad/s)

1. Calculate the rotational velocity of the imaginary centre wheel:

Wc = Sc/r

2. Calculate the turning circle to give the correct rotional velocity:

R = (Wc * r)/a'

3. Calculate the rotational speed of the two wheels:

Wo = Wc * ((0.5R+d)/0.5R)
Wi = Wc * ((0.5R-d)/0.5R)
