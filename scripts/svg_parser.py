import svgelements

from .prim import *

# TODO Everything...

def parse(file_path:str) -> list[Prim]:
    svg = svgelements.SVG.parse(file_path)
    types = set()
    for shape in svg.elements():
        if isinstance(shape, svgelements.svgelements.Path):
            for element in shape:
                if isinstance(element, svgelements.svgelements.Arc):
                    print(element.get_rotation().as_degrees)
                    print(element.get_rotation().as_gradians)
                    print(element.get_rotation().as_radians)
                    print()
                    
