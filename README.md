ZAutomate
=========

WSBF's radio automation system, vintage 2011.

## Installation

Ubuntu:
```
sudo apt-get install python python-tk python-tksnack python-pymad python-pyao pylint
git clone https://github.com/wsbf/ZAutomate.git
```

## Development

```
pylint **/*.py > lint.out
```

## TODO

- make Auto-Slot Rotation work
- review layering/communication between Player, Cart, and GridObj
- separate Logbook_Log into log_cart and log_track
- create separate classes for carts and tracks
- resolve lint errors
- Automation stops playing PSAs after a long time?
- Cart Machine buttons must be pressed 2-3 times to play
- Large queries in DJ Studio interrupt audio streaming (use multiprocess)
- Consider combining the three modules into one window
- sort through the three player modules
