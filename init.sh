#!/bin/bash
# Sample script to start/restart zautomate

killall python
app/za_automation.py &> za_automation.log &
app/za_cartmachine.py &> za_cartmachine.log &
app/za_studio.py &> za_studio.log &
