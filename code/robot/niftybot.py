#!/usr/bin/env python
'''
# niftybot.py #


Note: if you haven't already, read `README.txt`.


## About the documentation ##

I've decided that I'm going to extensively document every aspect of 
this codebase for several reasons:

    1.  It'd really suck if I'm the only person who understands the 
        how the code works
    2.  It'd be really cool if you guys are able to make changes to the
        codebase just as easily as I can (things get done faster!)
        
Therefore, feel free to modify either the documentation or the code
freely. Neither is meant to be permanent, and you should error on 
the side of making wild and radical changes. Don't worry about
breaking things -- we have version control, so if something breaks,
we can easily roll back.
        
I've also taken care to try and organize the code in a logical and 
orderly manner, almost like a book. Each module can be thought of 
as a "chapter", and for the most part, you should be able to just read
the comments one after the other without having to scroll and jump 
around in random places.

The documentation itself is written in a format called [Markdown][md],
a ridiculously simple plain text formatting syntax. It's deliberately
designed to be simple, so you don't really need to read the provided
link to understand how it works, but I provided it just in case you 
want to edit the documentation somewhere and want to make sure it's
consistent.

  [md]: http://daringfireball.net/projects/markdown/

  
## Introduction ##

This is the main file which starts everything. On the surface, it doesn't
contain much code. Rather, it loads up a bunch of other modules, and uses 
them one after the other to operate the robot. The logic and the bulk of
the code lives inside the modules, not inside here.

Each module can conceptually be thought of as a "layer" within this
program. Here are the current layers we have (warning: subject to change):

    1.  hardware           -- directly controls the Arduino on the lowest
                              level possible
    2.  sensor_analysis    -- analyzes sensor data (camera, encoders, etc)
    3.  robot_actions      -- provides functions to easily control the robot
                              using the hardware layer and data from the 
                              sensor_analysis layer
    4.  decision_making    -- provides high-level logic to make the robot 
                              independently make decisions
    5.  user_interface     -- lets humans control the robot

Each layer is meant to control only a single aspect of the code. The 
hardware layer, for example, is meant to directly control the individual
motors and actuators while the decision-making layer acts as the "brain"
that controls the robot.

Each layer must be kept as separate as possible from the other layers.
This is called [separation of concerns][soc], and helps keep the code clean.
By keeping layers separate, and exposing only well-defined functions
to interface between them, we are free to tweak and adjust any layer 
in the system without disrupting the others. In the most extreme 
case, we should be able to completely rip out and rewrite a layer 
without making changes to the rest of the code base.

  [soc]: https://en.wikipedia.org/wiki/Separation_of_concerns

In addition, lower layers should never be aware of what is occurring
at the higher levels. For example, while it's acceptable for the 
`robot_actions` layer to use the `basic_hardware` and `sensor_analysis`
layers to provide functions like "move to nearest person" or 
"turn right by 90 degrees", the `robot_actions` layer should never 
know about the actual decisions and logic the `decision_making` layer
is using. Here are some more [detailed reasons][ll] why.

  [ll]: http://programmers.stackexchange.com/q/198783/45762
  
We also have an additional layer called `errors`. Strictly speaking, this
layer isn't part of the heirarchy listed above, and contains method to 
handle emergency error-handling or logging. Basically, it contains code
as part of a last-ditch effort to cleanly shut the program down and 
generate a log when the program encounters an error that it cannot 
recover from.
  
  
## Up next... ##

I recommend you continue reading downwards, and finish reading everything
in this file. Then, move on to the first layer (`basic_hardware`), then
the second (`sensor_analysis`), etc.
'''

# Note: the module name corresponds to the name of the file.
# The code you write in `batman.py` can be accessed by doing
# `import batman`.

# These modules are part of Python's standard library
import sys
import traceback

# These modules are ones that we wrote
import basic_hardware
import sensor_analysis
import robot_actions
import decision_making
import user_interface
import errors

import cv2

def main():
    '''
    Everything goes inside this function. The reason why I'm sticking
    everything inside this function and not within the main file is 
    so that if I ever need to use this file (`niftybot.py`) from another
    Python project, importing it will not automagically start up
    the robot and do weird things. 
    
    It also contains last-ditch error handling. If the code throws an 
    exception, it will be caught and logged here.
    '''
    if "--noisy" in sys.argv:
        user_interface.main()
    else:
        try:
            user_interface.main()
        except SystemExit:
            pass
        except Exception:
            error = traceback.format_exc()
            errors.log('Top-level exception: ' + error)
            errors.error('The program encountered an unexpected error.\n\n' + 
                'Please see "log.txt" for details.')
    
# The "if __name__ == '__main__' bit is a common idiom in Python.
# See [this Stackoverflow answer][mn] for details.
# 
#   [mn]: http://stackoverflow.com/a/419185
if __name__ == '__main__':
    main()
    