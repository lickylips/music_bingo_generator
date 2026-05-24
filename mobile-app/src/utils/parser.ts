// Playlist Parser Logic

export interface ParsedSong {
  title: string;
  artist: string;
}

/**
 * Parses content of an M3U file.
 * Supports #EXTINF for metadata or falls back to filenames.
 */
export const parseM3U = (fileContent: string): ParsedSong[] => {
  const songs: ParsedSong[] = [];
  const lines = fileContent.split(/\r?\n/);

  // Strategy 1: Look for #EXTINF metadata
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("#EXTINF:")) {
      // Expected format: #EXTINF:123, Artist - Title
      try {
        const info = trimmed.split(",")[1];
        if (info) {
          if (info.includes(" - ")) {
            const parts = info.split(" - ");
            // Handle cases where title might also contain " - "
            const artist = parts[0].trim();
            const title = parts.slice(1).join(" - ").trim();
            if (title) {
              songs.push({ title, artist });
            }
          } else {
            songs.push({ title: info.trim(), artist: "" });
          }
        }
      } catch (e) {
        console.warn("Failed to parse line:", line);
      }
    }
  }

  // Strategy 2: If no metadata found, look for filenames
  if (songs.length === 0) {
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) {
        continue;
      }

      // Likely a file path
      // Replace backslashes with forward slashes
      const normalized = trimmed.replace(/\\/g, "/");
      const filename = normalized.split("/").pop();

      if (filename) {
        // Remove extension
        const nameWithoutExt = filename.replace(/\.[^/.]+$/, "");
        songs.push({ title: nameWithoutExt, artist: "" });
      }
    }
  }

  return songs;
};
