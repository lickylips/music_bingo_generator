export interface YouTubeTrack {
  title: string;
  artist: string;
}

export interface YouTubeResponse {
  tracks: YouTubeTrack[];
  playlistName?: string;
}

export const getPlaylistIdFromUrl = (url: string): string | null => {
  try {
    const match = url.match(/[?&]list=([^&]+)/);
    return match ? match[1] : null;
  } catch (e) {
    return null;
  }
};

export const fetchYouTubePlaylist = async (playlistId: string): Promise<YouTubeResponse> => {
  // Use the new stable alias for the Vercel backend
  const url = `https://musicbingo-sable.vercel.app/api/playlist?id=${playlistId}`;

  console.log(`Fetching playlist via backend: ${playlistId}`);

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.error || response.statusText;
      throw new Error(`Backend Error: ${errorMsg}`);
    }

    // Our backend returns { tracks: [...] }
    if (!data.tracks || data.tracks.length === 0) {
      return { tracks: [] };
    }

    return {
      tracks: data.tracks,
      playlistName: data.playlistName
    };

  } catch (error) {
    console.error("YouTube Fetch Error:", error);
    throw error;
  }
};
