# bottango_playback_interface
Control Bottango through its Web API from python.

This python3.7+ module is made to interface with Bottango, a Hardware/Robot/Animatronics animation software created by Evan McMahon

## [What is Bottango](https://www.bottango.com/)

## Installation
Install through pip with

`pip install bottango_playback_interface`

## Usage
Start by creating your animations with Bottango, enable the Web API and enter the 'Animate' mode

Then from your python script

```python
from bottango_playback_interface import BottangoPlaybackInterface

bpi = BottangoPlaybackInterface("localhost", 59224)
bpi.play_animation("animation_name_to_play")
bpi.wait_animation_done()

```

### Methods
```python
bpi.play_animation("animation_name_to_play")     # Plays the animation with the corresponding name
bpi.pause_animation()                            # Pause the current animation
bpi.resume_animation()                           # Resume the current animation
bpi.get_playback_state()                         # Get various informations from bottango
bpi.wait_animation_done(timeout=max_wait_time)   # Wait until the animation is over before returning or the timeout runs out.
bpi.get_animation_list()                         # Returns an array with all available animation names
bpi.emergency_stop()                             # Turn off live mode from Bottango, must be reenable from there.
```


## Development
git clone this project

Create a new venv

`python3 -m venv --system-site-packages ./venv`

Source it

`source ./venv/bin/activate`

Install all dependancies with poetry

`poetry install`

Install git hooks

`pre-commit install`

### Upload to pypi

Source the venv

`source ./venv/bin/activate`

Install twine

`pip install twine`

Config your pypi credentials in the file `~/.pypirc`

```python
[pypi]
username = pypi_username
password = pypi_password
```

Run

```python
poetry install
twine check dist/*
twine upload dist/*
```
