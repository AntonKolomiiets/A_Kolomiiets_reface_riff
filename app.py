import streamlit as st
import math
import os
import sys
import typing as T

from util.spectrogram_params import SpectrogramParams
from util import util as streamlit_util


from video_processing.file_handler import handle_file_upload
from video_processing.video_splitter import split_video
from video_processing.audio_replacer import replace_audio
from video_processing.zip_creator import create_zip
from video_processing.get_duration import get_duration
from moviepy.editor import VideoFileClip

# Remove or adjust  if have import modules error in streamlit app
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'util'))


def main():
    st.title("Hi Reface!")

    
    with st.sidebar:
        st.header("Upload and Settings")
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
        
   
        # Model settings
        with st.expander("Model Settings"):
            
            device = streamlit_util.select_device(st.sidebar)
            extension = 'mp3' # Alternatively, if you need option for selection this can be replaced with: 
                              # extension = streamlit_util.select_audio_extension(st.sidebar)
            checkpoint = streamlit_util.select_checkpoint(st.sidebar)

            num_inference_steps = T.cast(int, st.number_input("Inference steps", value=30))
            guidance = st.number_input(
                "Guidance", value=7.0, help="How much the model listens to the text prompt"
            )
            scheduler = st.selectbox(
                "Scheduler",
                options=streamlit_util.SCHEDULER_OPTIONS,
                index=0,
                help="Which diffusion scheduler to use",
            )
            assert scheduler is not None

            use_20k = st.checkbox("Use 20kHz", value=False)

        if use_20k:
            params = SpectrogramParams(
                min_frequency=10,
                max_frequency=20000,
                sample_rate=44100,
                stereo=True,
        )
        else:
            params = SpectrogramParams(
                min_frequency=0,
                max_frequency=10000,
                stereo=False,
            )

        
        
        # Upload videdo file
        if video_file:
            video_path = handle_file_upload(video_file)
            video = VideoFileClip(video_path)

            # Define number of parts
            num_parts = st.number_input("Number of video parts", min_value=1, max_value=10, value=1)
            
            # Choose clip to replace music
            clip_with_audio = st.number_input("Clip number to add audio to", min_value=1)

            # Final render in colums
            num_columns = st.number_input("Number of columns", min_value=3)
            
            # Session state for part duration
            if "part_durations" not in st.session_state:
                st.session_state.part_durations = [0] * num_parts

            # Dynamic slider creation
            total_duration = video.duration
            part_durations = []
            accumulated_duration = 0.0

            st.write("### Select durations for each part (in seconds)")

            for i in range(num_parts - 1):
                min_value = accumulated_duration
                max_value = total_duration - (num_parts - i - 1)
                part_duration = st.slider(f"Part {i+1} duration", min_value=min_value, max_value=max_value, value=st.session_state.part_durations[i] + min_value, step=0.1)
                part_durations.append(part_duration - accumulated_duration)
                accumulated_duration = part_duration

            # The last "slider" to display last part duration
            remaining_duration = total_duration - accumulated_duration
            st.write(f"Part {num_parts} duration: {remaining_duration:.1f} seconds")
            part_durations.append(remaining_duration)
            st.session_state.part_durations = part_durations
            

            st.write(f"Selected durations: {part_durations}")

    zip_path = None

    with st.form("Inputs"):
        prompt = st.text_input("Prompt")
        negative_prompt = st.text_input("Negative prompt")

        row = st.columns(4)

        starting_seed = T.cast(
            int,
            row[1].number_input(
                "Seed",
                value=42,
                help="Change this to generate different variations",
            ),
        )

        seed = starting_seed

        if st.form_submit_button("Riff", type="primary"):
            if not prompt:
                st.info("Enter a prompt")
                return

            if video_file and prompt:
                try:
                    # Create output directory
                    output_dir = os.path.join(os.path.dirname(__file__), 'output')
                    os.makedirs(output_dir, exist_ok=True)

                    # Split video to clips
                    with st.spinner("Splitting clips..."):
                        clips = split_video(video, st.session_state.part_durations, output_dir)

                    # Get duration of selectet clip for audio replacement
                    width = get_duration(clips[clip_with_audio - 1])
                    
                    # Generate audio
                    image = streamlit_util.run_txt2img(
                        prompt=prompt,
                        num_inference_steps=num_inference_steps,
                        guidance=guidance,
                        negative_prompt=negative_prompt,
                        seed=seed,
                        width=width,
                        height=512,
                        checkpoint=checkpoint,
                        device=device,
                        scheduler=scheduler,
                    )

                    segment = streamlit_util.audio_segment_from_spectrogram_image(
                        image=image,
                        params=params,
                        device=device,
                    )

                    audio_path = streamlit_util.save_audio_file(segment, f"{prompt.replace(' ', '_')}_{seed}", extension, output_dir)
                    
                    if not os.path.exists(audio_path):
                        st.error(f"Audio file not found at path: {audio_path}")
                        return

                    # Replace audio and get the path of the new video
                    new_video_path = replace_audio(clips[clip_with_audio - 1], audio_path)
                    clips[clip_with_audio - 1] = new_video_path

                    # Create zip file
                    zip_path = create_zip(clips, output_dir)

                except Exception as e:
                        st.error(f"An error occurred: {e}")

            else:
                st.error("Please upload a video file and provide an audio prompt.")


    if zip_path:
        st.success("Processing complete! Download the clips below.")

        # Download clips
        with open(zip_path, "rb") as f:
            st.download_button("Download Clips", data=f, file_name="clips.zip")
        
        # Results in columns
        st.write("### Generated Clips:")
        columns = st.columns(num_columns)
        for i, clip in enumerate(clips):
            col = columns[i % num_columns]
            col.video(clip)

        
if __name__ == "__main__":
    main()