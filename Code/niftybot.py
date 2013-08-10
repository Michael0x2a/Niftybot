import core
import test_worker
import control_panel


def main():
    mailbox = core.Mailbox()
    mailbox.register_worker('test_worker', test_worker.TestWorker)
    mailbox.register_worker('control_panel', control_panel.ControlServer)
    mailbox.mainloop()
    
if __name__ == '__main__':
    main()