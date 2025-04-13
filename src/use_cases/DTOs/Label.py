import zope.interface

class Label(zope.interface.Interface):
    x_label = zope.interface.Attribute("X-axis label")
    y_label = zope.interface.Attribute("Y-axis label")
    z_label = zope.interface.Attribute("Z-axis label")

@zope.interface.implementer(Label)
class Label_Implementation:
    def __init__(self, x_label: str, y_label: str, z_label: str):
        self.x_label = x_label
        self.y_label = y_label
        self.z_label = z_label