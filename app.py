
import streamlit as st

from utils.pdf_service import create_notes_pdf
from services.transcript_service import get_transcript
from services.gemini_service import generate_notes


# ---------- Page configuration ----------
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


# ---------- Session state ----------
if "transcript_error" not in st.session_state:
    st.session_state.transcript_error = False

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "notes" not in st.session_state:
    st.session_state.notes = ""


# ---------- Page heading ----------
st.title("📚 YouTube AI Notes Studio")

st.write(
    "Turn YouTube videos into clear study notes, "
    "summaries, definitions, and revision questions."
)


# ---------- YouTube URL ----------
youtube_url = st.text_input(
    "Paste your YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=...",
)


# ---------- Get transcript automatically ----------
if st.button("Get Video Transcript"):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube URL.")

    else:
        try:
            with st.spinner("Retrieving transcript..."):
                transcript = get_transcript(youtube_url.strip())

            if not transcript or not transcript.strip():
                raise ValueError(
                    "The video returned an empty transcript."
                )

            st.session_state.transcript = transcript.strip()
            st.session_state.transcript_error = False
            st.session_state.notes = ""

            # Clear old widget values when loading new content.
            st.session_state.pop("transcript_preview", None)
            st.session_state.pop("edited_notes", None)
            st.session_state.pop("manual_transcript_input", None)

            st.success("Transcript retrieved successfully!")

        except Exception as error:
            st.session_state.transcript_error = True
            st.session_state.transcript = ""
            st.session_state.notes = ""

            st.session_state.pop("transcript_preview", None)
            st.session_state.pop("edited_notes", None)

            st.error(
                "Automatic transcript retrieval failed. "
                "You can paste the transcript manually below."
            )

            with st.expander("View technical error details"):
                st.code(str(error))


# ---------- Manual transcript fallback ----------
if st.session_state.transcript_error:
    st.divider()
    st.subheader("📝 Paste Transcript Manually")

    st.write(
        "YouTube or the transcript service may block automatic "
        "retrieval. You can still generate notes by pasting the "
        "video transcript here."
    )

    st.markdown(
        """
        **How to get the transcript:**
        1. Open the video on YouTube.
        2. Look for the video's **Show transcript** option.
        3. Copy the available transcript text.
        4. Paste it into the box below.
        """
    )

    with st.form("manual_transcript_form"):
        manual_transcript = st.text_area(
            "Paste your video transcript here",
            height=250,
            key="manual_transcript_input",
            placeholder="Paste the complete transcript here...",
        )

        use_manual_transcript = st.form_submit_button(
            "Use Pasted Transcript"
        )

    if use_manual_transcript:
        if manual_transcript.strip():
            st.session_state.transcript = manual_transcript.strip()
            st.session_state.transcript_error = False
            st.session_state.notes = ""

            st.session_state.pop("transcript_preview", None)
            st.session_state.pop("edited_notes", None)

            st.success("Transcript added successfully!")

            st.rerun()

        else:
            st.warning("Please paste a transcript before continuing.")


# ---------- Display transcript ----------
if st.session_state.transcript:
    st.divider()
    st.subheader("📄 Video Transcript")

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

            if not notes or not str(notes).strip():
                raise ValueError(
                    "Gemini returned empty notes. Please try again."
                )

            st.session_state.notes = str(notes).strip()
            st.session_state.pop("edited_notes", None)

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
                    "A temporary service error does not necessarily "
                    "mean that paid billing is required."
                )

            elif (
                "429" in error_message
                or "resource_exhausted" in error_message
                or "quota" in error_message
            ):
                st.warning(
                    "Gemini may have reached a usage limit. "
                    "Check your available quota and try again later. "
                    "Review your plan and limits before changing "
                    "billing settings."
                )

            else:
                st.error("Could not generate AI notes.")
                st.caption(str(error))

            with st.expander("View technical error details"):
                st.code(str(error))


# ---------- Preview and download notes ----------
if st.session_state.notes:
    st.divider()
    st.subheader("📚 Your AI Study Notes")

    edited_notes = st.text_area(
        "Preview and edit your notes",
        value=st.session_state.notes,
        height=450,
        key="edited_notes",
    )

    # Download as TXT
    st.download_button(
        "📄 Download Notes as TXT",
        data=edited_notes,
        file_name="youtube_study_notes.txt",
        mime="text/plain",
    )

    # Download as PDF
    try:
        pdf_data = create_notes_pdf(edited_notes)

        st.download_button(
            "📕 Download Notes as PDF",
            data=pdf_data,
            file_name="youtube_study_notes.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.warning(
            "Could not create the PDF. "
            "You can still download your notes as TXT."
        )

        with st.expander("View PDF error"):
            st.code(str(error))


# ---------- Transcript-only download ----------
if st.session_state.transcript and not st.session_state.notes:
    st.divider()
    st.subheader("💾 Save Your Transcript")

    st.info(
        "If Gemini is temporarily unavailable, you can still "
        "save the transcript and generate notes later."
    )

    st.download_button(
        "📥 Download Transcript as TXT",
        data=st.session_state.transcript,
        file_name="youtube_transcript.txt",
        mime="text/plain",
    )