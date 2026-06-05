import streamlit as st
import io
from playlist_parser import PlaylistParser
from generator import BingoGenerator
from renderer import PDFRenderer

def inject_premium_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        /* Global Font Override - Targets text elements safely to exclude icons from being broken */
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Custom app header hero banner */
        .hero-container {
            background: linear-gradient(135deg, #1f0c33 0%, #0c0414 100%);
            padding: 2.2rem;
            border-radius: 1.2rem;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(127, 0, 255, 0.12) 0%, transparent 60%);
            pointer-events: none;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(45deg, #FF007F, #7F00FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            opacity: 0.85;
            font-weight: 300;
        }

        /* Sidebar Custom Glassmorphism styling */
        [data-testid="stSidebar"] {
            background-color: #08030d !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 1rem;
        }

        /* Frosted container card styling for sidebar inputs */
        div.row-widget.stRadio, div.row-widget.stNumberInput, div.row-widget.stTextInput, div.row-widget.stCheckbox {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 1.1rem !important;
            border-radius: 1rem !important;
            margin-bottom: 1.1rem !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
        }
        div.row-widget.stRadio:hover, div.row-widget.stNumberInput:hover, div.row-widget.stTextInput:hover {
            border-color: rgba(255, 0, 127, 0.4) !important;
            box-shadow: 0 4px 14px rgba(255, 0, 127, 0.12) !important;
        }

        /* Premium Custom File Uploader container cards */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 1.1rem !important;
            border-radius: 1rem !important;
            margin-bottom: 1.1rem !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
        }
        [data-testid="stFileUploader"] section {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px dashed rgba(255, 255, 255, 0.15) !important;
            border-radius: 0.8rem !important;
            padding: 1rem !important;
        }
        [data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, #7F00FF 0%, #FF007F 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            border-radius: 0.6rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 10px rgba(127, 0, 255, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stFileUploader"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 14px rgba(255, 0, 127, 0.3) !important;
            border: none !important;
        }

        /* Ensure high contrast text inside the file uploader box in all light/dark system modes */
        [data-testid="stFileUploader"] section p, 
        [data-testid="stFileUploader"] section span, 
        [data-testid="stFileUploader"] section small {
            color: #E0E0E0 !important;
            font-weight: 400 !important;
        }

        /* Force high contrast text and label visibility inside sidebar widgets */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] label p,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: #FFFFFF !important;
            font-weight: 500 !important;
            letter-spacing: 0.02em;
            margin-bottom: 0.4rem !important;
            display: inline-block;
        }

        /* Primary Button Styling */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #7F00FF 0%, #FF007F 100%) !important;
            color: white !important;
            border: none !important;
            padding: 0.6rem 2rem !important;
            border-radius: 0.8rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 15px rgba(127, 0, 255, 0.3) !important;
            transition: all 0.3s ease !important;
            width: 100%;
            margin-top: 0.5rem;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255, 0, 127, 0.4) !important;
        }
        div.stButton > button:first-child:active {
            transform: translateY(1px) !important;
        }

        /* Download Button CTA with Pulse */
        div.stDownloadButton > button:first-child {
            background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 2.8rem !important;
            border-radius: 0.8rem !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 18px rgba(0, 114, 255, 0.45) !important;
            transition: all 0.3s ease !important;
            animation: pulse 2s infinite;
            text-align: center;
            display: block;
            margin: 1.5rem auto !important;
        }
        div.stDownloadButton > button:first-child:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 198, 255, 0.55) !important;
        }

        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(0, 114, 255, 0.4);
            }
            70% {
                box-shadow: 0 0 0 14px rgba(0, 114, 255, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(0, 114, 255, 0);
            }
        }

        /* Playlist preview container cards */
        .song-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .song-card {
            background: rgba(128, 128, 128, 0.05);
            border: 1px solid rgba(128, 128, 128, 0.1);
            padding: 0.8rem;
            border-radius: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            transition: all 0.2s ease;
        }
        .song-card:hover {
            background: rgba(128, 128, 128, 0.1);
            border-color: rgba(255, 0, 127, 0.3);
            transform: translateX(4px);
        }
        .song-index {
            background: linear-gradient(135deg, #7F00FF, #FF007F);
            color: white;
            font-weight: 600;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            flex-shrink: 0;
        }
        .song-info {
            flex-grow: 1;
            overflow: hidden;
        }
        .song-title {
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-color, inherit);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .song-artist {
            font-size: 0.78rem;
            color: var(--text-color, inherit);
            opacity: 0.7;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .song-artist-badge {
            background: rgba(255, 0, 127, 0.15);
            color: #ff85be;
            padding: 0.05rem 0.35rem;
            border-radius: 0.3rem;
            font-size: 0.65rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Music Bingo Generator", page_icon="🎵")
    inject_premium_styles()

    # Premium Hero Header
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🎵 Music Bingo Generator</div>
            <div class="hero-subtitle">Instantly generate professional, randomized, print-ready PDF bingo cards from your playlists</div>
        </div>
    """, unsafe_allow_html=True)

    # -- Sidebar Configuration --
    st.sidebar.header("Configuration")
    source_type = st.sidebar.radio("Select Source", ["Local Playlist (M3U/WPL)", "YouTube Music URL"])

    playlist_data = []
    
    # -- Input Handling --
    if "Local" in source_type:
        uploaded_file = st.sidebar.file_uploader("Upload playlist file", type=["m3u", "m3u8", "wpl"])
        if uploaded_file:
            # Parse immediately to show preview
            string_data = uploaded_file.getvalue().decode("utf-8")
            parser = PlaylistParser()
            if uploaded_file.name.lower().endswith(".wpl"):
                playlist_data = parser.parse_wpl(string_data)
            else:
                playlist_data = parser.parse_m3u(string_data)
                
            if playlist_data:
                st.sidebar.success(f"Loaded {len(playlist_data)} songs.")
            else:
                st.sidebar.error("Could not find songs in the file.")
                
    else:
        yt_url = st.sidebar.text_input("YouTube Music Playlist URL")
        if yt_url:
            if st.sidebar.button("Fetch Playlist"):
                with st.spinner("Fetching metadata from YouTube Music..."):
                    parser = PlaylistParser()
                    playlist_data, playlist_name = parser.parse_youtube(yt_url)
                    if playlist_data:
                        st.sidebar.success(f"Loaded {len(playlist_data)} songs.")
                        st.session_state['playlist_data'] = playlist_data
                        st.session_state['playlist_name'] = playlist_name
                    else:
                        st.sidebar.error("Could not fetch playlist. Check URL or privacy settings.")
    
    # Retrieve from session state if available (for YouTube flow)
    if 'playlist_data' in st.session_state and not playlist_data:
        playlist_data = st.session_state['playlist_data']
        # If user switched back to M3U, we might have stale data. 
        # But for now let's assume simple flow.

    # -- Settings --
    st.sidebar.subheader("Output Settings")
    
    # Suggest a default title based on playlist if available
    default_title = "Music Bingo"
    if 'playlist_name' in st.session_state and st.session_state['playlist_name']:
        default_title = f"{st.session_state['playlist_name']}"
    elif "Local" in source_type and uploaded_file:
        # Simple extraction from filename
        fname = uploaded_file.name
        if "." in fname:
            fname = ".".join(fname.split(".")[:-1])
        default_title = f"{fname}"

    playlist_name = st.sidebar.text_input("Playlist Name", value=default_title)
    title_suffix = st.sidebar.text_input("Title Suffix", value="Round 1")
    
    page_size = st.sidebar.selectbox("Page Size", ["A3", "A4", "A5", "Letter", "Legal"], index=1)
    
    cards_options = ["1", "2", "4"]
    if page_size == "A3":
        cards_options = ["1", "2", "4", "6", "8"]
    elif page_size == "A5":
        cards_options = ["1", "2"]
        
    cards_per_sheet_str = st.sidebar.selectbox("Cards per Sheet", cards_options, index=1 if len(cards_options) > 1 else 0)
    cards_per_sheet = int(cards_per_sheet_str)
    
    num_cards = st.sidebar.number_input("Number of Cards", min_value=1, value=10, step=1)

    include_artist = st.sidebar.checkbox("Include Artist Names", value=True)
    jackpot = st.sidebar.checkbox("Jackpot Mode (No Free Space)", value=False)

    # -- Main Area --
    if playlist_data:
        st.subheader("✨ Preview Loaded Tracks")
        with st.expander("Show Song List Preview", expanded=True):
            song_cards_html = '<div class="song-grid">'
            for idx, s in enumerate(playlist_data[:12]):
                artist_badge = f'<span class="song-artist-badge">{s["artist"]}</span>' if s["artist"] else ''
                song_cards_html += f'<div class="song-card"><div class="song-index">{idx + 1}</div><div class="song-info"><div class="song-title" title="{s["title"]}">{s["title"]}</div><div class="song-artist">{s["artist"] if s["artist"] else "No Artist"} {artist_badge}</div></div></div>'
            song_cards_html += '</div>'
            st.markdown(song_cards_html, unsafe_allow_html=True)
            if len(playlist_data) > 12:
                st.markdown(f"<div style='text-align: center; color: #888; margin-top: 5px; margin-bottom: 10px; font-weight: 500;'>... and {len(playlist_data)-12} more songs in the playlist.</div>", unsafe_allow_html=True)

        generate_btn = st.button("Generate Bingo Sheets", type="primary")
        
        if generate_btn:
            generator = BingoGenerator()
            renderer = PDFRenderer()
            
            try:
                with st.spinner("Generating Bingo Cards..."):
                    # 1. Generate Grids
                    cards = generator.generate_cards(playlist_data, num_cards, jackpot=jackpot)
                    
                    # 2. Render PDF
                    pdf_buffer = renderer.render_to_bytes(
                        cards, 
                        title=playlist_name,
                        suffix=title_suffix,
                        page_size_name=page_size,
                        cards_per_sheet=cards_per_sheet,
                        include_artist=include_artist, 
                        jackpot=jackpot
                    )
                    
                    # 3. Success & Download
                    num_pages = (num_cards + cards_per_sheet - 1) // cards_per_sheet
                    st.success(f"Successfully generated {num_cards} cards on {num_pages} pages!")
                    
                    st.download_button(
                        label="Download PDF 📥",
                        data=pdf_buffer,
                        file_name="music_bingo.pdf",
                        mime="application/pdf"
                    )
            
            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    else:
        st.info("👈 Please upload a file or enter a URL to start.")

if __name__ == "__main__":
    main()