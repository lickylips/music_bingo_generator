// api/playlist.ts
// Standard Serverless Function using CommonJS and native fetch (Node 18+)

// Fallback to process.env, but allowing debug if env is missing
const API_KEY = process.env.YOUTUBE_API_KEY;

export default async function handler(req, res) {
  // enable CORS
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { id } = req.query;

  if (!id) {
    return res.status(400).json({ error: 'Missing playlist ID' });
  }

  // Debug check: If key is missing, return specific error
  if (!API_KEY) {
      console.error("Missing YOUTUBE_API_KEY env var");
      return res.status(500).json({ error: 'Server Config Error: API Key missing' });
  }

  try {
    const tracks = await fetchAllPlaylistItems(id);
    let playlistName = "YouTube Playlist";
    try {
      playlistName = await fetchPlaylistName(id);
    } catch (e) {
      console.warn("Failed to fetch playlist name:", e);
    }
    return res.status(200).json({ tracks, playlistName });
  } catch (error) {
    console.error('API Error:', error);
    return res.status(500).json({ error: error.message || 'Failed to fetch playlist' });
  }
}

async function fetchPlaylistName(playlistId) {
  const url = `https://www.googleapis.com/youtube/v3/playlists?part=snippet&id=${playlistId}&key=${API_KEY}`;
  const response = await fetch(url);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error?.message || 'YouTube API Error');
  }

  if (data.items && data.items.length > 0) {
    return data.items[0].snippet?.title || "YouTube Playlist";
  }
  return "YouTube Playlist";
}

async function fetchAllPlaylistItems(playlistId) {
  let items = [];
  let nextPageToken = '';
  const baseUrl = 'https://www.googleapis.com/youtube/v3/playlistItems';

  // Loop to fetch all pages
  do {
    const url = `${baseUrl}?part=snippet&maxResults=50&playlistId=${playlistId}&key=${API_KEY}&pageToken=${nextPageToken}`;
    
    // Use native fetch (Node 18+)
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error?.message || 'YouTube API Error');
    }

    if (data.items) {
      items = items.concat(data.items);
    }

    nextPageToken = data.nextPageToken || '';

  } while (nextPageToken);

  // Transform
  return items.map((item) => {
      const snippet = item.snippet;
      const title = snippet.title || "Unknown Title";
      let finalTitle = title;
      let finalArtist = snippet.videoOwnerChannelTitle || snippet.channelTitle || "Unknown Artist";

      if (title.includes(" - ")) {
        const parts = title.split(" - ");
        finalArtist = parts[0].trim();
        finalTitle = parts.slice(1).join(" - ").trim();
      }

      return {
        title: finalTitle,
        artist: finalArtist
      };
  });
}