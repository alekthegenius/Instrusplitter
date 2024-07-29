import streamlit as st
import demucs
from pydub import AudioSegment

st.logo("icon.jpg")
st.title("Instrusplitter")
st.subheader("Splits Audio Tracks Using Demucs")

if "model" not in st.session_state:
    st.session_state.model = "htdemucs"
if "adv_settingd" not in st.session_state:
    st.session_state.adv_settingd = False
if "input_method" not in st.session_state:
    st.session_state.input_method = ""

st.session_state.uploaded_files = ""

with st.sidebar:
    st.title("Settings")

    st.session_state.adv_settingd = st.toggle("Advanced Settings", value=False)

    with st.form("Settings"):

        with st.expander("Models"):
            st.session_state.model = st.radio(
                "Model",
                ["htdemucs", "hdemucs_ft", "htdemucs_6s", "htdemucs_mmi", "mdx", "mdx_extra", "mdx_q", "mdx_extra_q", "SIG"],
                captions=[
                    "first version of Hybrid Transformer Demucs. Trained on MusDB + 800 songs. Default model.",
                    "fine-tuned version of htdemucs, separation will take 4 times more time but might be a bit better. Same training set as htdemucs.",
                    "6 sources version of htdemucs, with piano and guitar being added as sources. Note that the piano source is not working great at the moment.",
                    "Hybrid Demucs v3, retrained on MusDB + 800 songs.",
                    "trained only on MusDB HQ, winning model on track A at the MDX challenge.",
                    "trained with extra training data (including MusDB test set), ranked 2nd on the track B of the MDX challenge.",
                    "quantized version of the previous models. Smaller download and storage but quality can be slightly worse.",
                    "quantized version of the previous models. Smaller download and storage but quality can be slightly worse.",
                    "where SIG is a single model from the model zoo.",
                ]
            )

        with st.expander("Search Settings"):
            pass

        if st.session_state.adv_settingd:
           with st.expander("Advanced Settings"):
               pass


        st.form_submit_button("Updated Settings")

if st.session_state.input_method == "Search":
    st.session_state.input_method = st.selectbox(
        "Input Method:",
        ("Search", "Upload File"),
        index=0
    )
else:
    st.session_state.input_method = st.selectbox(
        "Input Method:",
        ("Search", "Upload File"),
        index=1
    )


with st.form("input"):
    if st.session_state.input_method == "Search":
        st.session_state.uploaded_files = st.text_input("Search", key="search")
    else:
        st.session_state.uploaded_files = st.file_uploader("Upload File", type=["wav", "mp3", "mp4", "aac"], key="upload")

    split_music_button = st.form_submit_button("Split Music")

if split_music_button:
    if st.session_state.uploaded_files is not None:
        print(st.session_state.uploaded_files)
        for uploaded_file in st.session_state.uploaded_files:
                    if uploaded_file.name.endswith(".mp3"):
                        file = AudioSegment.from_mp3(file)
                        format = "audio/mp3"
                    
                    st.audio(uploaded_file, format=format)


