import zope.interface

class AX_Label(zope.interface.Interface):
    x_label = zope.interface.Attribute("X-axis label")
    y_label = zope.interface.Attribute("Y-axis label")
    title = zope.interface.Attribute("Title of the chart")

@zope.interface.implementer(AX_Label)
class AX_LabelImplementation:
    def __init__(self, x_label: str, y_label: str, title: str):
        self.x_label = x_label
        self.y_label = y_label
        self.title = title