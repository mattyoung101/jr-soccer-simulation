# Team Omicron RoboCup Jr Simulation
This is the repo for Team Omicron in the February 2021 RoboCup Jr Simulation competition.

Link to the [upstream codebase](https://github.com/RoboCupJuniorTC/rcj-soccer-sim) this repo is based on.

Team members: Ethan Lo, Matt Young, James Talkington.

## Features
- Finite state machine
    - Attacker, defender and midfielder roles
    - Fine tuned strategies over a few weeks of development
- Inter-robot communications
    - Achieved through inter-process communication (IPC) over TCP using Python's `multiprocessing.connection` module
        - Cannot mount an additional receiver to the Webots robot - hence this setup
    - Used to achieve role switching
    - [Confirmed to be legal](https://github.com/RoboCupJuniorTC/rcj-soccer-sim/issues/29#issuecomment-760452442) in the
    February 2021 competition (Please check the rules for each individual competition, we take no responsibility for compliance
    with future rule changes!)
- Ball velocity estimation
- Ball position prediction up to 2 seconds in the future
- Fully modelled tank drive steering
- Efficient, circular orbit

## Licence
All code written by us is released under the Mozilla Public License v2.0, see LICENSE.txt.

If you use this repo in your own robot, please give credit to Team Omicron and Ethan Lo, Matt Young and James Talkington.
Any modifications to MPL'd files must be released under the MPL as well (new files do not have this requirement).

If the MPL's legalese is too difficult to read, try [this FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/), 
and [this question](https://opensource.stackexchange.com/a/8832) for a better explanation.

## Concluding remarks
Hopefully this will be a high-performing robot base that other teams can use in the future.

Some things we wanted to add but didn't get time to do (might be worth implementing these yourself):

- Wall awareness (planning to avoid hitting walls)
- Robot awareness (planning to drive around our teammates)
- 

If you have any questions or comments, feel free to open an issue on this repo. Thanks, and have fun.