import pygame
import pygame.camera

def main():
    pygame.init()
    pygame.camera.init()
    
    cam_list = pygame.camera.list_cameras()
    print cam_list
    
    cam = pygame.camera.Camera(cam_list[0], (640, 480))
    print cam
    
    cam.start()
    
    screen = pygame.display.set_mode((640, 480))
    snapshot = pygame.surface.Surface((640, 480), 0, screen)
    
    while True:
        snapshot = cam.get_image(screen)
        screen.blit(screen, (0, 0))
        
        pygame.display.flip()
        
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            cam.stop()
            pygame.quit()
            break
            
    print "done"
    
if __name__ == '__main__':
    main()
    
    

