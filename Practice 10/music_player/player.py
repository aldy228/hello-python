import pygame
import os

class MusicPlayer:
    """Handles music playback and playlist management"""
    
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.tracks = []
        self.current_index = 0
        self.is_playing = False
        self.load_tracks(music_folder)
    
    def load_tracks(self, folder):
        """Load all MP3/WAV files from folder"""
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(('.mp3', '.wav')):
                    full_path = os.path.join(folder, file)
                    self.tracks.append(full_path)
            print(f"Loaded {len(self.tracks)} tracks from {folder}")
    
    def play(self):
        """Play current track"""
        if self.tracks:
            pygame.mixer.music.load(self.tracks[self.current_index])
            pygame.mixer.music.play()
            self.is_playing = True
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def next_track(self):
        """Play next track in playlist"""
        if self.tracks:
            self.current_index = (self.current_index + 1) % len(self.tracks)
            self.play()
    
    def prev_track(self):
        """Play previous track in playlist"""
        if self.tracks:
            self.current_index = (self.current_index - 1) % len(self.tracks)
            self.play()
    
    def get_current_name(self):
        """Get current track filename"""
        if self.tracks:
            return os.path.basename(self.tracks[self.current_index])
        return "No tracks loaded"
    
    def get_track_count(self):
        """Get total number of tracks"""
        return len(self.tracks)
    
    def get_current_index(self):
        """Get current track number (1-based)"""
        return self.current_index + 1 if self.tracks else 0
    
    def get_position(self):
        """Get current playback position in seconds"""
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0