import streamlit as st
import demucs.api
import numpy as np
from tempfile import NamedTemporaryFile
import torch
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os


st.logo("icon.jpg")
st.title("Instrusplitter")
st.subheader("Splits Audio Tracks Using Demucs")

if "model" not in st.session_state:
    st.session_state.model = "htdemucs"
if "adv_settingd" not in st.session_state:
    st.session_state.adv_settingd = False
if "input_method" not in st.session_state:
    st.session_state.input_method = ""
if "segment" not in st.session_state:
    st.session_state.segment = None
if "split" not in st.session_state:
    st.session_state.split = False
if "device" not in st.session_state:
    st.session_state.device = "cuda" if torch.cuda.is_available() else "cpu"
if "file_format" not in st.session_state:
    st.session_state.file_format = ".mp3"
if "splitted_files" not in st.session_state:
    st.session_state.splitted_files = {}
if "jobs" not in st.session_state:
    st.session_state.jobs = 0

st.session_state.mixing = False

st.cache_data.clear()
st.cache_resource.clear()

dir_name = "/tmp/"
dir = os.listdir(dir_name)

for item in dir:
    if item.endswith(".mp3"):
        os.remove(os.path.join(dir_name, item))

separator = demucs.api.Separator(model=st.session_state.model)

st.session_state.uploaded_files = ""

with st.sidebar:
    st.title("Settings")

    st.session_state.adv_settingd = st.toggle("Advanced Settings", value=False)

    with st.form("Settings"):

        with st.expander("Models"):
            st.session_state.model = st.radio(
                "Model",
                ["htdemucs", "htdemucs_ft", "htdemucs_6s", "hdemucs_mmi", "mdx", "mdx_extra", "mdx_q", "mdx_extra_q",],
                captions=[
                    "first version of Hybrid Transformer Demucs. Trained on MusDB + 800 songs. Default model.",
                    "fine-tuned version of htdemucs, separation will take 4 times more time but might be a bit better. Same training set as htdemucs.",
                    "6 sources version of htdemucs, with piano and guitar being added as sources. Note that the piano source is not working great at the moment.",
                    "Hybrid Demucs v3, retrained on MusDB + 800 songs.",
                    "trained only on MusDB HQ, winning model on track A at the MDX challenge.",
                    "trained with extra training data (including MusDB test set), ranked 2nd on the track B of the MDX challenge.",
                    "quantized version of the previous models. Smaller download and storage but quality can be slightly worse.",
                    "quantized version of the previous models. Smaller download and storage but quality can be slightly worse.",
                ]
            )

        with st.expander("Format"):
            st.session_state.file_format = st.selectbox(
                "Choose your perferred audio format for the exported file:",
                (".mp3", ".wav"),
            )

        if st.session_state.adv_settingd:
           with st.expander("Advanced Settings"):
                
                st.markdown("Segment: Length (in seconds) of each segment (Set to Zero for None)")
            
                st.session_state.segment = st.slider("Segment", min_value=0, max_value=100, value=st.session_state.segment, step=1)

                st.markdown("Device (torch.device, str, or None): If provided, device on which to execute the computation, otherwise wav.device is assumed. When device is different from wav.device, only local computations will be on device, while the entire tracks will be stored on wav.device. If not specified, will use the command line option.")

                st.session_state.device = st.text_input("Device", placeholder="torch.device, str, or None", value=st.session_state.device)

                st.markdown("Jobs: Number of jobs. This can increase memory usage but will be much faster when multiple cores are available. If not specified, will use the command line option. Only available when device = cpu")

                st.session_state.jobs =  st.slider("Jobs", min_value=0, max_value=len(os.sched_getaffinity(0)), value=st.session_state.jobs, step=1)


               


        adv_submit_button = st.form_submit_button("Updated Settings")

    if adv_submit_button:
        with st.spinner("Updating Settings"):
            if st.session_state.segment == 0:
                separator.update_parameter(split=True, segment=st.session_state.segment, device=st.session_state.device, jobs=st.session_state.jobs)
            else:
                separator.update_parameter(split=False, segment=None, device=st.session_state.jobs, jobs=st.session_state.jobs)



st.session_state.input_method = st.selectbox(
        "Input Method:",
        ("Youtube URL", "Upload Files"),
    )

def download_video():
    link = str(st.session_state.search)

    try:
        yt = YouTube(link, on_progress_callback=on_progress)
        streams = yt.streams.filter(only_audio=True)
    except Exception as e:
        st.exception(e)

    for stream in streams:
        st.code(stream, language="python")

    


with st.container(border=True):
    st.subheader(st.session_state.input_method)

    if st.session_state.input_method == "Youtube URL":
        st.session_state.uploaded_files = st.text_input("Youtube URL", key="search", label_visibility="collapsed")


    else:
        st.session_state.uploaded_files = st.file_uploader("Upload Files", type=["wav", "mp3"], accept_multiple_files=True, label_visibility="collapsed")

    split_music_button = st.button("Split Music")


if split_music_button:
    if st.session_state.uploaded_files != []:
        st.session_state.splitted_files = {}

        if st.session_state.input_method == "Youtube URL":
            with st.spinner("Splitting Files..."):
                link = str(st.session_state.uploaded_files)

                try:
                    yt = YouTube(link, on_progress_callback=on_progress)
                    ys = yt.streams.get_audio_only()

                    audio = NamedTemporaryFile(suffix=".mp3", delete=False)

                    audio_path = ys.download(filename=audio.name[5:-4], output_path=audio.name[:5], mp3=True)
                    origin, separated = separator.separate_audio_file(audio_path)


                    st.markdown(f"Original Audio: {audio.name}")
                    st.audio(audio_path, format="audio/mpeg")

                    for stem, source in separated.items():

                        output_file = NamedTemporaryFile(suffix=".mp3", delete=False)

                        demucs.api.save_audio(source, output_file.name, samplerate=separator.samplerate)

                        output_file.seek(0)

                        file_name = f"{stem}-{audio.name[5:]}"

                        mime = "audio/mpeg"

                        audio_data = output_file.read()
                        
                        st.session_state.splitted_files[file_name] = audio_data

                        st.markdown(f"{stem}")
                        st.audio(output_file.name, format=mime)
                        st.download_button(f"Download '{file_name}'", data=audio_data, file_name=file_name, mime=mime, key=int(f"{list(separated).index(stem)}"))
                except Exception as e:
                    st.exception(e)
                




        else:
            with st.spinner("Splitting Files..."):

                for uploaded_file in st.session_state.uploaded_files:
                            with st.container(border=True):

                                st.subheader("Splitted Files")

                                if uploaded_file.name.endswith(".mp3"):
                                    uploaded_file_format = ".mp3"
                                elif uploaded_file.name.endswith(".wav"):
                                    uploaded_file_format = ".wav"


                                audio = NamedTemporaryFile(suffix=uploaded_file_format, delete=False)

                                

                                audio.write(uploaded_file.getvalue())


                                audio.seek(0)

                                origin, separated = separator.separate_audio_file(audio.name)

                                st.markdown(f"Original Audio: {uploaded_file.name}")
                                st.audio(audio.name, format=uploaded_file.type)

                                for stem, source in separated.items():

                                    output_file = NamedTemporaryFile(suffix=st.session_state.file_format, delete=False)

                                    demucs.api.save_audio(source, output_file.name, samplerate=separator.samplerate)

                                    output_file.seek(0)

                                    file_name = f"{st.session_state.uploaded_files.index(uploaded_file)}-{stem}-{uploaded_file.name}" if st.session_state.uploaded_files.index(uploaded_file) >= 1 else f"{stem}-{uploaded_file.name}"

                                    mime = "audio/mpeg" if st.session_state.file_format == ".mp3" else "audio/wav"

                                    audio_data = output_file.read()
                                    
                                    st.session_state.splitted_files[file_name] = audio_data

                                    st.markdown(f"{stem}")
                                    st.audio(output_file.name, format=mime)
                                    st.download_button(f"Download '{file_name}'", data=audio_data, file_name=file_name, mime=mime, key=int(f"{st.session_state.uploaded_files.index(uploaded_file)}{list(separated).index(stem)}"))
                                
                                print(st.session_state.splitted_files.keys())

                                  
            st.balloons()

if st.button("Mix Splitted Tracks", use_container_width=True):
    if len(st.session_state.splitted_files) > 0:
        st.switch_page("pages/mix.py")


            
                    


