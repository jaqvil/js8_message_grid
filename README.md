## Preamble
I enjoy HAM radio a lot and the JS8 modulation scheme just makes sense.
Able to get CW type distances on a digital mode that implents FEC?
Wow is all I can say.

Anyhow, I set up my HF rig in the Netherlands at our first rental home and was so happy to hear so much traffic on air.
But digging through the JS8Call application interface to see which new stations are around and what the HAMs chatted about was a pain.

So I heard about the JS8Net parser below and decided to push what was heard to a DB and pull some of that info to a simple webpage just to have a quick look once or twice a day who is chatting.

#### Mega thanks
Using the jfrancis42/js8net github parser as found at [https://github.com/jfrancis42/js8net]

**js8_get_msgs** is the script that'll connect to your [JS8Call](http://js8call.com/) app's TCP port and log msgs to the dB

**js8_web** is the python flask webserver that'll query the dB and display the info for you

_from the JS8Call webpage_
[![JS8Call on laptop](http://js8call.com/wp-content/uploads/2019/12/IMG_20191024_203533_050.jpg)]
