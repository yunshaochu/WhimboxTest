import numpy as np
from whimbox.map.convert import *
    

class NikkiPosition():
    def __init__(self,position) -> None:
        if isinstance(position,list):
            self.position=np.array(position)
        else:
            self.position=position

        self.px = self._get_px_position()
        self.game = self._get_game_location()

    def _get_px_position(self):
        pass

    def _get_game_location(self):
        pass

class PxPostion(NikkiPosition):
    def __init__(self,position) -> None:
        super().__init__(position)

    def _get_px_position(self):
        return self.position

    def _get_game_location(self):
        return convert_PngMapPx_to_GameLoc(self.position)
    
class GameLocation(NikkiPosition):
    def __init__(self,position) -> None:
        super().__init__(position)

    def _get_px_position(self):
        return convert_GameLoc_to_PngMapPx(self.position)

    def _get_game_location(self):
        return self.position