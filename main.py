import pygame as pg

from components.button import Button
from components.card import Card

class App:
    WIDTH: int = 800
    HEIGHT: int = 600
    FPS: int = 60

    def __init__(self) -> None:
        pg.init()
        pg.display.set_caption('Pygame App')
        self.screen: pg.Surface = pg.display.set_mode(
            (self.WIDTH, self.HEIGHT)
        )
        self.clock: pg.time.Clock = pg.time.Clock()

        self.button1 = Button(
            text='Quit',
            pos=(self.WIDTH // 2, self.HEIGHT // 2),
            size=(160, 60),
        )
        
        self.button2 = Card(
            text='Button 2',
            pos=(20, 20),
            size=(40, 40),
        )

        self.running: bool = True

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(self.FPS)
        
        self._shutdown()

    def _handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            self.button1.handle_event(event, on_click=self._quit)
            self.button2.handle_event(event, on_click=lambda: print('Button 2 clicked!'))
    
    def _update(self) -> None:
        pass

    def _draw(self) -> None:
        self.screen.fill((30, 30, 30))
        self.button1.draw(self.screen)
        self.button2.draw(self.screen)
        pg.display.flip()

    def _quit(self) -> None:
        self.running = False
    
    def _shutdown(self) -> None:
        pg.quit()

if __name__ == '__main__':
    app = App()
    app.run()
