import streamlit as st
import demucs.api
from pydub import AudioSegment
import numpy as np
from tempfile import NamedTemporaryFile
import torch
from io import BytesIO

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
if "jobs" not in st.session_state:
    st.session_state.jobs = 6
if "file_format" not in st.session_state:
    st.session_state.file_format = ".mp3"
if "splitted_files" not in st.session_state:
    st.session_state.splitted_files = {}

st.session_state.mixing = False

st.cache_data.clear()
st.cache_resource.clear()

separator = demucs.api.Separator(model=st.session_state.model)

st.session_state.uploaded_files = ""

with st.sidebar:
    st.title("Settings")

    st.session_state.adv_settingd = st.toggle("Advanced Settings", value=False)

    with st.form("Settings"):

        with st.expander("Models"):
            st.session_state.model = st.radio(
                "Model",
                ["htdemucs", "hdemucs_ft", "htdemucs_6s", "htdemucs_mmi", "mdx", "mdx_extra", "mdx_q", "mdx_extra_q",],
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

        with st.expander("Search Settings"):
            pass

        if st.session_state.adv_settingd:
           with st.expander("Advanced Settings"):

               st.session_state.segment = st.slider("Segment", min_value=0, max_value=100, value=st.session_state.segment, step=1)

               st.session_state.device = st.text_input("Device", placeholder="torch.device, str, or None", value=st.session_state.device)


               


        adv_submit_button = st.form_submit_button("Updated Settings")

    if adv_submit_button:

        if st.session_state.segment == 0:
            separator.update_parameter(split=True, segment=st.session_state.segment, device=st.session_state.device)
        else:
            separator.update_parameter(split=False, segment=None, device=st.session_state.device)



st.session_state.input_method = st.selectbox(
        "Input Method:",
        ("Search", "Upload Files"),
    )


with st.form("input"):
    st.subheader(st.session_state.input_method)

    if st.session_state.input_method == "Search":
        st.session_state.uploaded_files = st.text_input("Search", key="search", label_visibility="collapsed")
    else:
        st.session_state.uploaded_files = st.file_uploader("Upload Files", type=["wav", "mp3"], accept_multiple_files=True, label_visibility="collapsed")

    split_music_button = st.form_submit_button("Split Music")


if split_music_button:
    if st.session_state.uploaded_files != []:
        
        print(st.session_state.uploaded_files)
        with st.spinner("Splitting Files..."):

            
            st.session_state.splitted_files = {}

            for uploaded_file in st.session_state.uploaded_files:
                        with st.container(border=True):

                            st.subheader("Splitted Files")

                            if uploaded_file.name.endswith(".mp3"):
                                uploaded_file_format = ".mp3"
                            elif uploaded_file.name.endswith(".wav"):
                                uploaded_file_format = ".wav"


                            audio = NamedTemporaryFile(suffix=uploaded_file_format)

                            

                            audio.write(uploaded_file.getvalue())


                            audio.seek(0)

                            origin, separated = separator.separate_audio_file(audio.name)

                            st.markdown(f"Original Audio: {uploaded_file.name}")
                            st.audio(audio.name, format=uploaded_file.type)

                            for stem, source in separated.items():

                                output_file = NamedTemporaryFile(suffix=st.session_state.file_format)

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
        on_click=st.switch_page("pages/mix.py")


            
                    


