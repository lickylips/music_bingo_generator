import re
from ytmusicapi import YTMusic

class PlaylistParser:
    def parse_m3u(self, file_content_str):
        """
        Parses content of an M3U file (passed as string).
        Supports #EXTINF for metadata or falls back to filenames.
        """
        songs = []
        lines = file_content_str.splitlines()
        
        # Strategy 1: Look for #EXTINF metadata
        for line in lines:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                # Expected format: #EXTINF:123, Artist - Title
                try:
                    # Split after the first comma
                    info = line.split(",", 1)[1]
                    if " - " in info:
                        parts = info.split(" - ", 1)
                        artist = parts[0].strip()
                        title = parts[1].strip()
                    else:
                        artist = ""
                        title = info.strip()
                    
                    if title:
                        songs.append({"title": title, "artist": artist})
                except IndexError:
                    continue

        # Strategy 2: If no metadata found, look for filenames
        if not songs:
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # It's likely a file path
                # Extract filename from path
                # FIXED: Escaped backslash correctly
                filename = line.replace(chr(92), "/").split("/")[-1]
                # Remove extension
                if "." in filename:
                    filename = ".".join(filename.split(".")[:-1])
                
                if filename:
                    songs.append({"title": filename, "artist": ""})
        
        return songs

    def parse_youtube(self, url):
        """Fetches metadata from a YouTube Music playlist."""
        songs = []
        playlist_title = ""
        try:
            yt = YTMusic()
            # Extract playlist ID
            playlist_id = url
            if "list=" in url:
                playlist_id = url.split("list=")[1].split("&")[0]
            
            playlist = yt.get_playlist(playlist_id)
            playlist_title = playlist.get('title', '')
            if 'tracks' not in playlist:
                return [], ""
                
            for track in playlist['tracks']:
                title = track.get('title', 'Unknown')
                artists_list = track.get('artists', [])
                artist = ", ".join([a['name'] for a in artists_list]) if artists_list else ""
                songs.append({'title': title, 'artist': artist})
                
        except Exception as e:
            # Propagate error or return empty? Let's print for now.
            print(f"Error parsing YouTube: {e}")
            return [], ""
            
        return songs, playlist_title

    def parse_wpl(self, file_content_str):
        """
        Parses content of a WPL (Windows Media Player Playlist) file.
        Extracts song titles and artists from <media src="..." /> tags.
        """
        import xml.etree.ElementTree as ET
        songs = []
        try:
            # Parse XML string
            root = ET.fromstring(file_content_str)
            
            # Locate all <media> elements
            for media in root.findall(".//media"):
                src = media.get("src")
                if not src:
                    continue
                    
                # Normalize path delimiters and get the file name
                filename = src.replace("\\", "/").split("/")[-1]
                
                # Strip file extension
                if "." in filename:
                    filename = ".".join(filename.split(".")[:-1])
                    
                if filename:
                    if " - " in filename:
                        parts = filename.split(" - ", 1)
                        artist = parts[0].strip()
                        title = parts[1].strip()
                    else:
                        artist = ""
                        title = filename.strip()
                        
                    songs.append({"title": title, "artist": artist})
        except Exception as e:
            print(f"Error parsing WPL playlist: {e}")
            
        return songs

