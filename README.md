# Mus-Comp: Enabling Music For Everyone
At Mus-Comp, our goal is two-fold: 1) allow musicians and hobbyists to quickly attain separated-instrument audio files and a MIDI file for music production and resampling, and 2) allow developers to carry forward our work and make it better.

## Our Work from 10,000 Feet Above
Like our goal, our work is two-fold as well:

**Task 1:** In one hand, we have the task of training a machine-learning model to classify and separate instruments playing in an audio file. Then, we have to take those separated-instrument audio files and construct a MIDI file from it.

**Task 2:** On the other hand, we have the task of developing a user-friendly website that can host our trained model and allow people to use it without any hassle.

## Open-Source Tools We Use
1) [Spleeter](https://github.com/deezer/spleeter) - a library that provides the model architecture and training pipeline (using tensorflow backend) that allows us to train a custom model for source separation. Under the hood, Spleeter creates [spectograms](https://pnsn.org/spectrograms/what-is-a-spectrogram#:~:text=A%20spectrogram%20is%20a%20visual,energy%20levels%20vary%20over%20time.) for each instrument you want to train and learns classification from them using a [UNET architecture](https://paperswithcode.com/method/u-net#:~:text=U%2DNet%20is%20an%20architecture,architecture%20of%20a%20convolutional%20network.).
2) 

## Limitations of Spleeter
1) The major limitation of the current pretrained models that Spleeter has to offer is the lack of variation in instruments. Currently, Spleeter has a "5Stems" model (trained on around 100 songs) that can classify and separate 3 instruments (not including vocals): piano, drums, and bass. We want to extend this classification boundary to 12 instruments: `Electric_Bass_pick, Glockenspiel, Bright_Acoustic_Piano, Rock_Organ, String_Ensemble_1, Distortion_Guitar, Brass_Section, Electric_Grand_Piano, Electric_Guitar_clean, Acoustic_Guitar_nylon, Violin, Drums`
2) The other major limitation of Spleeter is that it is relatively difficult to use as configuration steps for training a custom model are not explained clearly (even in the presence of a dedicated wiki page).

## The Data Processing Challenge
The main challenge of completing **Task 1** is *gathering* quality music data, *storing* it in a normalized manner, and *preprocessing* it for Spleeter's training pipeline.
### Gathering
We use the publicly available [Slakh2100](http://www.slakh.com/) Dataset for training our source-separation model. This dataset contains 2100 mixed tracks with their corresponding MIDI files.
### Preprocessing
Here is the directory layout of Slakh2100 ([source](https://github.com/ethman/slakh-utils#metadata)): 
```
Track00001
   └─── all_src.mid
   └─── metadata.yaml
   └─── MIDI
   │    └─── S01.mid
   │    │    ...
   │    └─── SXX.mid
   └─── mix.flac
   └─── stems
        └─── S01.flac
        │    ...
        └─── SXX.flac 
```
This extends for all 2100 tracks. For **Task 1** we need a mapping of a track's `mix.flac` (actually converted to `.wav`) to all it's stem files: `[S01.flac,...,SXX.flac]` (also converted to `.wav`). However, in doing this, we need to label what instrument each stem file is representing because the numerical-prefixes are not consistently mapped to specific instruments. We acheive this mapping by parsing the `metadata.yaml` file present within every track, which contains which instrument a stem file represents.

We then generate two `.csv` files as required by Spleeter's traning pipeline. Both files will contain paths for a `mix` audio file and its corresponding instruments in a single row. However, one file will be used for model *training* and the other for *validation*.
Here is an example of one row: 
| Mix_path  | Electric_Bass_pick_path | Glockenspiel_path | ... | Duration |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| path/to/slakh2100_00028_-1.wav  | path/to/slakh2100_00028_Electric Bass pick.wav  |  | ... | 255.3379819 |
