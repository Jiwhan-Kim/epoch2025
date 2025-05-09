from . import Button

import pygame as pg
from utils.colors import WHITE, BLACK

from typing import Tuple

class Card(Button):
    def __init__(
        self,
        text: str,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        *,
        bg_color: Tuple[int, int, int] = WHITE,
        text_color: Tuple[int, int, int] = BLACK,
        border_radius: int = 16,
        outline_color: Tuple[int, int, int] = BLACK,
        outline_width: int = 2,
    ) -> None:
        super().__init__(
            text=text,
            pos=pos,
            size=size,
            bg_color=bg_color,
            text_color=text_color,
            border_radius=border_radius,
        )
        self.outline_color = outline_color
        self.outline_width = outline_width
    
    def draw(self, surface: pg.Surface) -> None:
        pg.draw.rect(
            surface, self.bg_color, self.rect, border_radius=self.border_radius
        )
        pg.draw.rect(
            surface,
            self.outline_color,
            self.rect,
            width=self.outline_width,
            border_radius=self.border_radius,
        )
        if self._text_surf and self._text_rect:
            surface.blit(self._text_surf, self._text_rect)

