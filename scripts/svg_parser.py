import svgelements
from .prim import Arc, Bezier, Circle, Ellipse, Line, Prim

def parse(file_path:str) -> list[Prim]:
    svg = svgelements.SVG.parse(file_path)
    prims:list[Prim] = []

    for shape in svg.elements():
        if not isinstance(shape, svgelements.svgelements.Path):
            continue

        for element in shape:
            if isinstance(element, svgelements.svgelements.Arc):
                prims.append(Arc(
                    element.center,
                    element.radius,
                    element.get_start_angle().as_radians,
                    element.get_end_angle().as_radians,
                    element.get_rotation()
                ))
            elif isinstance(element, svgelements.svgelements.CubicBezier):
                prims.append(Bezier((
                    element.start,
                    element.control1,
                    element.control2,
                    element.end
                )))
            elif isinstance(element, svgelements.svgelements.Circle):
                prims.append(Circle(
                    (element.cx, element.cy),
                    element.rx
                ))
            elif isinstance(element, svgelements.svgelements.Ellipse):
                prims.append(Ellipse(
                    (element.cx, element.cy),
                    (element.rx, element.ry),
                    element.rotation
                ))
            elif isinstance(element, svgelements.svgelements.Line):
                prims.append(Line(
                    element.start,
                    element.end
                ))

    return prims
