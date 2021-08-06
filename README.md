# dirigent
Tool for orchestrating media players (mopidy, vlc) with a YAML playlist file, written in Python3 and tested on Raspberry 3 Model B (Rev 1.2) running Raspbian 10

The idea for this tool is to control multiple media players in a way that would normally require manual intervention. This allows to mix streaming media with file-based playback and to dynamically react to the used players.

This basic implementation uses mopidy to stream music from spotify and vlc to open media files.
The players are then controlled via playerctl, which uses the MPRIS D-Bus. As such, it is necessary to install the Mopidy-MPRIS package along with the other Mopidy backends you intend to use.

