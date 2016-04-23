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

- Migrate DBInterface to use the new PHP API
- Automation stops playing PSAs after a long time?
- Automation should only play songs currently in rotation
- Cart Machine buttons must be pressed 2-3 times to play
- Large queries in DJ Studio interrupt audio streaming (use multiprocess)
- Consider combining the three modules into one window
