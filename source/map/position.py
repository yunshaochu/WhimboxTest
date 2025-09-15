import numpy as np
from source.map.convert import *
    

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
        return convert_mapPx_to_gameLoc(self.position)
    
class GameLocation(NikkiPosition):
    def __init__(self,position) -> None:
        super().__init__(position)

    def _get_px_position(self):
        return convert_gameLoc_to_mapPx(self.position)

    def _get_game_location(self):
        return self.position