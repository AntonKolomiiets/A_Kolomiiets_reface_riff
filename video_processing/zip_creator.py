import zipfile
import os

def create_zip(clips, output_dir):
    """
    Create zip file with clips for download.
    """
    zip_path = os.path.join(output_dir, "clips.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for clip in clips:
            zipf.write(clip, os.path.basename(clip))
    return zip_path
