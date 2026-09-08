// Playlist Parser Logic

export interface ParsedSong {
  title: string;
  artist: string;
}

export const sanitizeTitle = (title: string): string => {
  const pattern = /\s*[\(\[][^\]\)]*(?:remaster|version|mix|edit|video|audio|lyrics|original|clip|live)[^\]\)]*[\)\]]/gi;
  let cleaned = title.replace(pattern, '');
  cleaned = cleaned.replace(/\s*[\(\[]\s*[\)\]]/g, '');
  return cleaned.trim();
};


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
              songs.push({ title: sanitizeTitle(title), artist });
            }
          } else {
            songs.push({ title: sanitizeTitle(info.trim()), artist: "" });
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
        songs.push({ title: sanitizeTitle(nameWithoutExt), artist: "" });
      }
    }
  }

  return songs;
};

/**
 * Parses content of a WPL file.
 * Extracts metadata from <media src="..." /> tags using a RegExp.
 */
export const parseWPL = (fileContent: string): ParsedSong[] => {
  const songs: ParsedSong[] = [];
  
  // Regex to match <media src="..."/> tags and capture the src attribute
  const mediaRegex = /<media\s+[^>]*\bsrc=[\"']([^\"']+)[\"']/gi;
  let match;
  
  while ((match = mediaRegex.exec(fileContent)) !== null) {
    const src = match[1];
    if (src) {
      // Normalize backslashes to forward slashes and grab file name
      const normalized = src.replace(/\\/g, "/");
      const filename = normalized.split("/").pop();
      
      if (filename) {
        // Remove extension
        const nameWithoutExt = filename.replace(/\.[^/.]+$/, "");
        
        if (nameWithoutExt.includes(" - ")) {
          const parts = nameWithoutExt.split(" - ");
          const artist = parts[0].trim();
          const title = parts.slice(1).join(" - ").trim();
          songs.push({ title: sanitizeTitle(title), artist });
        } else {
          songs.push({ title: sanitizeTitle(nameWithoutExt.trim()), artist: "" });
        }
      }
    }
  }
  
  return songs;
};

