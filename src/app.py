import streamlit as st
import io
from playlist_parser import PlaylistParser
from generator import BingoGenerator
from renderer import PDFRenderer

def main():
    st.set_page_config(page_title="Music Bingo Generator", page_icon="🎵")
    st.title("🎵 Music Bingo Generator")
    st.markdown("Generate printable PDF bingo sheets from your playlists.")

    # -- Sidebar Configuration --
    st.sidebar.header("Configuration")
    source_type = st.sidebar.radio("Select Source", ["Local M3U File", "YouTube Music URL"])

    playlist_data = []
    
    # -- Input Handling --
    if source_type == "Local M3U File":
        uploaded_file = st.sidebar.file_uploader("Upload .m3u file", type=["m3u", "m3u8"])
        if uploaded_file:
            # Parse immediately to show preview
            string_data = uploaded_file.getvalue().decode("utf-8")
            parser = PlaylistParser()
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
    num_pages = st.sidebar.number_input("Number of Pages (2 cards per page)", min_value=1, value=1, step=1)
    
    # Suggest a default title based on playlist if available
    default_title = "Music Bingo"
    if 'playlist_name' in st.session_state and st.session_state['playlist_name']:
        default_title = f"Music Bingo - {st.session_state['playlist_name']}"
    elif source_type == "Local M3U File" and uploaded_file:
        # Simple extraction from filename
        fname = uploaded_file.name
        if "." in fname:
            fname = ".".join(fname.split(".")[:-1])
        default_title = f"Music Bingo - {fname}"

    game_title = st.sidebar.text_input("Game Title", value=default_title)
    include_artist = st.sidebar.checkbox("Include Artist Names", value=True)

    # -- Main Area --
    if playlist_data:
        st.subheader("Preview Songs")
        with st.expander("Show Song List"):
            for s in playlist_data[:10]:
                st.text(f"{s['title']} - {s['artist']}")
            if len(playlist_data) > 10:
                st.text(f"... and {len(playlist_data)-10} more.")

        generate_btn = st.button("Generate Bingo Sheets", type="primary")
        
        if generate_btn:
            # Generate Logic
            num_cards = num_pages * 2
            
            generator = BingoGenerator()
            renderer = PDFRenderer()
            
            try:
                with st.spinner("Generating Bingo Cards..."):
                    # 1. Generate Grids
                    cards = generator.generate_cards(playlist_data, num_cards)
                    
                    # 2. Render PDF
                    pdf_buffer = renderer.render_to_bytes(cards, title=game_title, include_artist=include_artist)
                    
                    # 3. Success & Download
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