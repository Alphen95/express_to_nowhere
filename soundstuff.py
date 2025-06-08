from pydub import AudioSegment
from pydub.playback import play

sound = AudioSegment.from_file('ted1.wav', format="wav")

# shift the pitch up by half an octave (speed will increase proportionally)

for i in range(30):
    octaves = -1+0.1*i

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    hipitch_sound = hipitch_sound.set_frame_rate(44100)

    hipitch_sound.export(f"res/sound/engine_{i}.wav", format="wav")
    print(i)