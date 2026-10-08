
import streamlit as st

from utils.pdf_service import create_notes_pdf
from services.transcript_service import get_transcript
from services.gemini_service import generate_notes


st.set_page_config(
    page_title="YouTube AI Notes Studio",
    page_icon="📚",
    layout="wide",
)

# ---------- Purple theme ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f7f1ff, #eee5ff);
    }
    h1, h2, h3 {
        color: #6036a5;
    }
    .stButton > button {
        background-color: #7950c7;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 1rem;
    }
    .stButton > button:hover {
        background-color: #6036a5;
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Page heading ----------
st.title("📚 YouTube AI Notes Studio")
st.write(
    "Turn YouTube videos into clear study notes, "
    "summaries, definitions, and revision questions."
)

# ---------- Session state ----------
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "notes" not in st.session_state:
    st.session_state.notes = ""

# ---------- YouTube URL ----------
youtube_url = st.text_input(
    "Paste your YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

# ---------- Get transcript ----------
if st.button("Get Video Transcript"):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube URL.")
    else:
        try:
            with st.spinner("Retrieving transcript..."):
                transcript = get_transcript(youtube_url)

            st.session_state.transcript = transcript
            st.session_state.notes = ""
            st.success("Transcript retrieved successfully!")

        except Exception as error:
            st.error("Could not retrieve the transcript.")
            st.caption(str(error))

# ---------- Display transcript ----------
if st.session_state.transcript:
    st.subheader("Video Transcript")

    st.text_area(
        "Review the transcript",
        value=st.session_state.transcript,
        height=220,
        key="transcript_preview",
    )

    # ---------- Generate AI notes ----------
    if st.button("✨ Generate AI Study Notes"):
        try:
            with st.spinner(
                "Gemini is preparing your study notes..."
            ):
                notes = generate_notes(
                    st.session_state.transcript
                )

            st.session_state.notes = notes
            st.success("Your study notes are ready!")

        except Exception as error:
            error_message = str(error).lower()

            if (
                "503" in error_message
                or "service_unavailable" in error_message
                or "high demand" in error_message
            ):
                st.warning(
                    "Gemini is temporarily busy. "
                    "Please wait a minute or two and try again. "
                    "Paid billing is not required to resolve "
                    "a temporary service-unavailable error."
                )

            elif (
                "429" in error_message
                or "resource_exhausted" in error_message
                or "quota" in error_message
            ):
                st.warning(
                    "Gemini may have reached a usage limit. "
                    "Check your available free-tier quota and "
                    "try again later. Do not enable paid billing "
                    "just to resolve a quota error."
                )

            else:
                st.error("Could not generate AI notes.")
                st.caption(str(error))

            with st.expander("View technical error details"):
                st.code(str(error))

# ---------- Preview and download notes ----------
if st.session_state.notes:
    st.subheader("Your AI Study Notes")

    edited_notes = st.text_area(
        "Preview and edit your notes",
        value=st.session_state.notes,
        height=450,
        key="edited_notes",
    )

    st.download_button(
        "📄 Download Notes as TXT",
        data=edited_notes,
        file_name="youtube_study_notes.txt",
        mime="text/plain",
    )

    try:
        pdf_data = create_notes_pdf(edited_notes)

        st.download_button(
            "📕 Download Notes as PDF",
            data=pdf_data,
            file_name="youtube_study_notes.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.warning("Could not create the PDF. You can still download TXT.")
        with st.expander("View PDF error"):
            st.code(str(error))

# ---------- Transcript-only fallback ----------
if st.session_state.transcript and not st.session_state.notes:
    st.divider()
    st.subheader("Save your transcript")

    st.info(
        "If Gemini is temporarily unavailable, you can still "
        "save the transcript and try generating notes later."
    )

    st.download_button(
        "📥 Download Transcript as TXT",
        data=st.session_state.transcript,
        file_name="youtube_transcript.txt",
        mime="text/plain",
    )