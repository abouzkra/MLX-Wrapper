from enum import Enum

from .base import Asset
from .sprite import Sprite
from ..exceptions import AssetError


class LoopMode(Enum):
    """Loop mode for the animated sprite.

    Attributes:
        LOOP (int): Loop the animation.
        PINGPONG (int): Ping-pong the animation.
        ONCE (int): Play the animation once.

    """

    LOOP = 0
    PINGPONG = 1
    ONCE = 2


class AnimatedSprite(Asset):
    """A simple implementation of animated sprites.

    Attributes:
        frames (list[Sprite]): List of frames for the animation.
        loop_mode (LoopMode): Loop mode for the animation.
        current_index (int): Current frame index.
        ping_pong_dir (int): Ping-pong direction.
        elapsed_time (float): Elapsed time since the animation started.
        frame_time (float): Time between frames.
        is_playing (bool): Whether the animation is playing.
        is_finished (bool): Whether the animation is finished (used for
            ONCE loop mode).

    """

    def __init__(
        self,
        frames: list[Sprite],
        fps: int = 12,
        loop_mode: LoopMode = LoopMode.LOOP,
    ) -> None:
        """Initialize an animated sprite with the given frames, frames per
        second, and loop mode.

        Args:
            frames (list[Sprite]): List of frames for the animation.
            fps (int): Frames per second.
            loop_mode (LoopMode): Loop mode for the animation. Defaults to
                LoopMode.LOOP.
        """
        if not frames:
            raise AssetError("AnimatedSprite needs at least one frame.")

        if fps <= 0:
            raise AssetError("fps must be greater than 0.")

        self.frames: list[Sprite] = frames
        self.loop_mode: LoopMode = loop_mode

        self.current_index: int = 0
        self.ping_pong_dir: int = 1  # 1 = forward, -1 = backward

        self.elapsed_time: float = 0.0
        self.frame_time: float = 1.0 / fps if fps > 0 else 0.0
        self.is_playing: bool = False
        self.is_finished: bool = False

    def reset(self) -> None:
        """Reset the animation to the beginning."""
        self.current_index = 0
        self.is_finished = False

    def play(self) -> None:
        """Play the animation."""
        self.is_playing = True

    def pause(self) -> None:
        """Pause the animation."""
        self.is_playing = False

    def stop(self) -> None:
        """Stop the animation."""
        self.is_playing = False
        self.reset()

    def update(self, dt: float) -> None:
        """Update the animation state based on the elapsed time.

        Args:
            dt (float): The elapsed time since the last update.

        """
        if not self.is_playing or len(self.frames) <= 1:
            return

        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_time:
            self.elapsed_time %= self.frame_time
            self._next_frame()

    def _next_frame(self) -> None:
        """Advance to the next frame based on the loop mode."""
        n_frames = len(self.frames)

        match self.loop_mode:
            case LoopMode.LOOP:
                self.current_index = (self.current_index + 1) % n_frames
            case LoopMode.PINGPONG:
                self.current_index += self.ping_pong_dir
                if self.current_index >= n_frames - 1:
                    self.current_index = n_frames - 1
                    self.ping_pong_dir = -1
                elif self.current_index <= 0:
                    self.current_index = 0
                    self.ping_pong_dir = 1
            case LoopMode.ONCE:
                if self.current_index < n_frames - 1:
                    self.current_index += 1
                else:
                    self.is_playing = False
                    self.is_finished = True

    def blit(self, target: Sprite, x: int, y: int) -> None:
        """Blit the current frame onto the target sprite at (x, y).

        Args:
            target (Sprite): The target sprite to blit onto.
            x (int): The x-coordinate of the target position.
            y (int): The y-coordinate of the target position.

        """
        self.frames[self.current_index].blit(target, x, y)

    def _custom_destroy(self) -> None:
        """Destroy the animated sprite, freeing its resources."""

        for f in self.frames:
            f.destroy()
