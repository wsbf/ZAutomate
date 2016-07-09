ZAutomate
=========

WSBF's radio automation system, vintage 2011.

## Installation

Ubuntu:

    sudo apt-get install python python-tk python-tksnack python-pymad python-pyao pylint
    git clone https://github.com/wsbf/ZAutomate.git

## Development

    pylint **/*.py > lint.log

## TODO

- move colors, fonts, text values to constants
- review cart_queue for design flaws, possible infinite loop?
- separate Logbook_Log into log_cart and log_track
- create separate classes for carts and tracks
- clean up print statements, use `logging` module
- add hourly reload to Cart Machine
- Large queries in DJ Studio interrupt audio streaming (use multiprocess)
- Consider combining the three modules into one window
