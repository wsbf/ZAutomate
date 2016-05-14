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
pylint **/*.py > lint.log
```

## TODO

- consider making a Grid class
- implement zautomate_log.php in the new API
- move colors, fonts, text values to constants
- add hourly reload to Cart Machine
- analyze the insertion/removal of carts, thread management during Automation
- separate Logbook_Log into log_cart and log_track
- create separate classes for carts and tracks
- resolve lint errors
- clean up print statements, use `logging` module
- Automation stops playing PSAs after a long time?
- Large queries in DJ Studio interrupt audio streaming (use multiprocess)
- Consider combining the three modules into one window
