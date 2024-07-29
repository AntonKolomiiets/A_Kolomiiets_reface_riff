# Hi Reface!

Here is a Streamlit application for processing video files. This project allows users to upload videos, generate audio from text prompts, and replace the audio in the video clips.

## Features

- Upload video files in mp4 or avi format.
- Split videos into multiple parts with custom duration.
- Generate audio from text prompts.
- Replace audio in video clips with generated audio.
- Download processed video clips.

## Exra

The model used in this app can be found here: https://huggingface.co/riffusion/riffusion-model-v1 and Riffusion pipline.

Custom clip duration selector allows choosing the exact duration (in seconds) of each part of the video for more control over the final result. Although it might not be the most intuitive on the first try, it is largely implemented that way due to limitations of the Streamlit API.

WARNING! Adding additional parts too fast (double or triple clicking on "+") can result in an "IndexError: list index out of range." To resolve this, just revert back to one part and add parts at a moderate speed.

For testing, I used "high-pitched sound, vocals, bad quality sound, low quality sound, noise" as the negative prompt, with a seed of 43 and all other settings set to default.

## Installation

To run the application locally, clone the repo from GitHub with `git clone`, install dependencies with `pip install -r requirements.txt` and run with `streamlit run app.py`

## Sugesstions

With Streamlit i could not find reliable library to make use of browser's local storage to store Prompt and model values, to prevent acident delition or settings lost. And as I'm also familiar with JavaScrypt, If we used somethin like React for interface, we could open mode features to prompt engeneers and also help them manage their work better.