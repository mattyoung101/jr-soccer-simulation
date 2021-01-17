# Team Omicron RoboCup Jr Simulation
This is the repo for Team Omicron in the February 2021 RoboCup Jr Simulation competition.

Team members: Ethan Lo, Matt Young, James Talkington.

## Features
- Finite state machine
    - Attacker, defender and midfielder roles
- Inter-robot communications
    - Achieved using inter-process communication (IPC) over TCP
    - Uses JSON
    - Used to achieve role switching
- Ball velocity estimation
- Ball position prediction up to 2 seconds in the future
- Fully modelled tank drive steering
- Efficient, circular orbit

## Licence
All code written by us is released under the Mozilla Public License v2.0, see LICENSE.txt.
