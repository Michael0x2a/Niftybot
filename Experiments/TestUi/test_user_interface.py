from kivy.app import App
from kivy.uix.widget import Widget

class ManualControl(Widget):
    pass
    
class InspectionView(Widget):
    pass
    
class LogView(Widget):
    pass
    
class StateView(Widget):
    pass
    

class CameraView(Widget):
    pass
    
class ProximityView(Widget):
    pass
    
class SensorView(Widget):
    pass

    
class ControlPanelApp(App):
    def build(self):
        return SensorView()
        
    
if __name__ == '__main__':
    ControlPanelApp().run()
    
    
        
        