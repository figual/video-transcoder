import subprocess

def transcode(input_path, output_path, codec, bitrate, resolution):
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", codec, "-b:v", bitrate, "-s", resolution,
        output_path
    ]
    subprocess.run(command)
    return output_path

