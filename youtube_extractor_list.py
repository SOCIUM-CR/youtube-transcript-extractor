from pytube import Playlist
import sys
import urllib.parse

def extract_playlist_urls(playlist_url, output_file="youtube_urls.txt"):
    """
    Extract all video URLs from a YouTube playlist and save them to a text file.
    
    Args:
        playlist_url (str): The URL of the YouTube playlist
        output_file (str): The name of the file to save the URLs (default: youtube_urls.txt)
    """
    try:
        # Clean and parse the URL
        cleaned_url = urllib.parse.unquote(playlist_url)
        
        # Extract playlist ID
        if 'list=' not in cleaned_url:
            raise ValueError("No playlist ID found in URL. Please provide a valid playlist URL.")
            
        # Create a Playlist object
        playlist = Playlist(cleaned_url)
        
        # Get all video URLs from the playlist
        video_urls = playlist.video_urls
        
        if not video_urls:
            raise ValueError("No videos found in playlist. Please check if the playlist is public and accessible.")
        
        # Write URLs to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in video_urls:
                f.write(url + '\n')
        
        print(f"Successfully extracted {len(video_urls)} URLs to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if playlist URL is provided as command line argument
    if len(sys.argv) > 1:
        playlist_url = sys.argv[1]
        # Use custom output file name if provided
        output_file = sys.argv[2] if len(sys.argv) > 2 else "youtube_urls.txt"
        extract_playlist_urls(playlist_url, output_file)
    else:
        print("Please provide a YouTube playlist URL as an argument")
        print("Usage: python youtube_extractor_list.py \"<playlist_url>\" [output_file]")
        sys.exit(1)