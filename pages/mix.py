import streamlit as st
from pydub import AudioSegment
from tempfile import NamedTemporaryFile

if "mixing" not in st.session_state:
    st.session_state.mixing = False
if "splitted_files" not in st.session_state:
    st.session_state.splitted_files = {}

st.logo("icon.jpg")
st.title("Mixer")
st.subheader("Mix Audio Tracks")


if "mixing" not in st.session_state:
    st.session_state.mixing = False

@st.dialog("🚨ERROR: No splitted files found")
def no_files_found(error=None):
    if error == None:
        st.markdown("**Error: No splitted files found.** Please split files first, then try again.")
        st.page_link("app.py", label="Go back to the home page")
    else:
        st.markdown("**Error: No splitted files found.** Please split files first, then try again.")
        st.exception(error)
        st.page_link("app.py", label="Go back to the home page")



try:
    print(st.session_state.splitted_files.keys())
    if st.session_state.splitted_files != {}:
        if st.session_state.mixing:
            print("MIXING")
            mixed_audio = AudioSegment.empty()

            print(st.session_state.selected.values())
            print(st.session_state.splitted_files.keys())

            with NamedTemporaryFile(suffix=st.session_state.file_format, delete=False) as first_file:
                if st.session_state.file_format == ".mp3":
                    first_file.write(list(st.session_state.splitted_files.values())[0])
                    mixed_audio = AudioSegment.from_mp3(first_file.name)
                    mixed_audio = mixed_audio.apply_gain(+int(list(st.session_state.gains.values())[0])) if list(st.session_state.gains.values())[0] >= 0 else mixed_audio.apply_gain(int(list(st.session_state.gains.values())[0]))
                else:
                    first_file.write(list(st.session_state.splitted_files.values())[0])
                    mixed_audio = AudioSegment.from_wav(first_file.name)
                    mixed_audio = mixed_audio.apply_gain(+int(list(st.session_state.gains.values())[0])) if list(st.session_state.gains.values())[0] >= 0 else mixed_audio.apply_gain(int(list(st.session_state.gains.values())[0]))

            for select, source, gain in zip(list(st.session_state.selected.values())[1:], list(st.session_state.splitted_files.values())[1:], list(st.session_state.gains.values())[1:]):
                if select:
                    with NamedTemporaryFile(suffix=st.session_state.file_format, delete=False) as temp_file:
                        temp_file.write(source)

                        if st.session_state.file_format == ".mp3":

                            sound = AudioSegment.from_mp3(temp_file.name)
                            mixed_audio = mixed_audio.overlay(sound, gain_during_overlay=gain)
                        else:

                            sound = AudioSegment.from_wav(temp_file.name)
                            mixed_audio = mixed_audio.overlay(sound, gain_during_overlay=gain)

                        st.session_state.overlay_sources.append(sound)

            with NamedTemporaryFile(suffix=st.session_state.file_format, delete=False) as export_mix:
                mixed_audio.export(export_mix, format=st.session_state.file_format[1:])
                export_mix.seek(0)
                st.markdown(f"MIXED AUDIO")
                print(export_mix.name)
                st.audio(export_mix.read(), format="audio/mpeg" if st.session_state.file_format == '.mp3' else "audio/wav")
                st.download_button(f"Download Mix File", data=export_mix.read(), file_name="mix_file.mp3", mime=st.session_state.file_format[1:])
                st.session_state.mixing = False
            
            if st.button("Return to Mixer Panel", use_container_width=True):
                st.session_state.mixing = False

            
        else:
            print("SELECTING")
            st.session_state.selected = {}
            st.session_state.gains = {}
            st.names = st.session_state.splitted_files.keys()
            st.session_state.overlay_sources = []

            with st.form("Mix Panel"):
                for name, source in st.session_state.splitted_files.items():
                    st.subheader(name)
                    st.session_state.selected[name] = st.checkbox("Select", key=name)
                    st.session_state.gains[name] = st.slider("Change Gain", min_value=-100, max_value=100, value=0, step=1, key=(name+"gain"))
                    st.audio(source, format="audio/mpeg" if st.session_state.file_format == '.mp3' else "audio/wav")
            

                mix_submit_button = st.form_submit_button("Mix")

            if mix_submit_button:
                print(st.session_state.selected.keys())
                if sum(st.session_state.selected.values()) > 1:
                    st.toast("Click Again to Mix")
                    st.session_state.mixing = True
                else:
                    st.toast("Please select at least two files to mix")
                    st.session_state.mixing = False
            




    else:
        no_files_found()
        st.markdown("**Error: No splitted files found.** Please split files first, then try again.")

except AttributeError as e:
    no_files_found(e)
    st.markdown("**Error: No splitted files found.** Please split files first, then try again.")