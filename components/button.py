from __future__ import annotations
import os
import pygame as pg
from typing import Callable, Tuple

from utils.colors import WHITE, BLACK, RED, GREEN, BLUE


class Button:
    def __init__(
            self,
            text: str,
            pos: Tuple[int, int],
            size: Tuple[int, int],
            *,
            font: str | os.PathLike | None = './assets/PretendardVariable.ttf',
            font_size: int = 24,
            bg_color: Tuple[int, int, int] = WHITE,
            text_color: Tuple[int, int, int] = BLACK,
            border_radius: int = 0,
    ) -> None:
        self.text = text
        self.rect = pg.Rect(0, 0, *size)
        self.rect.center = pos
        
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        
        self.font = self._load_font(font, font_size)
        self._render_text()
    
    @staticmethod
    def _load_font(font: str | os.PathLike | None, size: int) -> pg.font.Font:
        if font is None:
            return pg.font.Font(None, size)
        
        font = os.fspath(font)
        if os.path.isfile(font):
            return pg.font.Font(font, size)
        
        return pg.font.SysFont(font, size)

    def _render_text(self) -> None:
        if self.text:
            self._text_surf = self.font.render(self.text, True, self.text_color)
            self._text_rect = self._text_surf.get_rect(center=self.rect.center)
        else:
            self._text_surf = None
            self._text_rect = None

    def draw(self, surface: pg.Surface) -> None:
        pg.draw.rect(
            surface, self.bg_color, self.rect, border_radius=self.border_radius
        )
        if self._text_surf and self._text_rect:
            surface.blit(self._text_surf, self._text_rect)

    def handle_event(
        self, event: pg.event.Event, *, on_click: Callable[[], None] | None = None
    ) -> None:
        if (
            on_click
            and event.type == pg.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ): on_click()

