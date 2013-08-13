import core

import test_worker
import control_panel
import camera_feed

def main():
    mailbox = core.Mailbox()
    '''
    mailbox.register_worker(
        'test_worker', 
        test_worker.TestWorker,
        optional="hello world")
    ''' 
    mailbox.register_worker(
        'control_panel', 
        control_panel.ControlServer)
    
    mailbox.register_worker(
        'camera_feed',
        camera_feed.CameraFeed)
    
    mailbox.register_worker(
        'camera_analysis',
        camera_feed.CameraAnalysis)
    
        
    mailbox.mainloop()
    
if __name__ == '__main__':
    main()