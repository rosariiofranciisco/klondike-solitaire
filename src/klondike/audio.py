
from pathlib import Path

import pygame


class GameAudio:
    """Manage background music and sound effects."""

    def __init__(self) -> None:
        self.music_volume = 0.5
        self.sound_volume = 0.5
        self.music_enabled = True
        self.sound_enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}


    def play_music(self) -> None:
        """Load and play the background music."""
        music_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "music"
            / "background.mp3"
        )

        pygame.mixer.music.load(str(music_path))
        pygame.mixer.music.set_volume(self.music_volume)

        if self.music_enabled:
            pygame.mixer.music.play(-1)


    def load_sounds(self) -> None:
        """Load all sound effects."""
        sounds_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "sounds"
        )

        sound_names = (
            "click",
            "draw",
            "move",
            "flip",
            "victory",
            "game_over",
        )

        for name in sound_names:
            sound_path = sounds_path / f"{name}.wav"
            self.sounds[name] = pygame.mixer.Sound(str(sound_path))

    def play_sound(self, name: str) -> None:
        """Play a sound effect if sound is enabled."""
        if not self.sound_enabled:
            return

        sound = self.sounds.get(name)

        if sound is not None:
            sound.set_volume(self.sound_volume)
            sound.play()

    def toggle_music(self) -> None:
        """Toggle background music on or off."""
        self.music_enabled = not self.music_enabled

        if self.music_enabled:
            pygame.mixer.music.unpause()

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()

    def toggle_sound(self) -> None:
        """Toggle sound effects on or off."""
        self.sound_enabled = not self.sound_enabled

    def set_music_volume(self, volume: float) -> None:
        """Set the background music volume."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sound_volume(self, volume: float) -> None:
        """Set the sound effects volume."""
        self.sound_volume = max(0.0, min(1.0, volume))