# bottango_playback_interface
Control Bottango through its Web API from python

## Installation
Install through pip with

`pip install bottango_playback_interface`

## Usage
Start by creating your animations with Bottango. Enable the Web API.

Then from your python script

```python
from bottango_playback_interface import BottangoPlaybackInterface

bpi = BottangoPlaybackInterface("localhost", 59224)
bpi.play_animation(`animation_name_to_play`)
bpi.wait_animation_done()

```

### Methods
```python
bpi.play_animation(`animation_name_to_play`)
bpi.pause_animation()
bpi.get_playback_state()
bpi.wait_animation_done(timeout=`max_wait_time`)
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

Install twine

`pip install twine`

Run

```python
twine check dist/*
twine upload dist/*
```
