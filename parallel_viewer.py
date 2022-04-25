import multiprocessing as mp
import numpy as np
import pygame
pygame.init()
N = 512

def read_rand(n):
    with open("/dev/urandom", "rb") as f:
        buf = f.read(n*n*3)
        lin_arr = np.frombuffer(buf, dtype=np.uint8)
        array = lin_arr.reshape((n, n, 3))
    return array

def refresh_image(queue, comm_queue):
    while True:
        if not comm_queue.empty():
            status = comm_queue.get()
            if status == "stop":
                # Torna a posar l'estat perquè la resta de processos el llegeixin
                comm_queue.put(status)
                break
        # Llegim imatge desde /dev/urandom
        image = read_rand(N)
        # Envia les dades a l'altre procés
        queue.put_nowait(image)
    print("Finished reading images")
    return

def show_image(queue, comm_queue, display):
    # Iniciem una finestra...
    disp_arr = pygame.surfarray.pixels3d(display)
    while True:
        if not comm_queue.empty():
            status = comm_queue.get()
            if status == "stop":
                # Torna a posar l'estat perquè la resta de processos el llegeixin
                comm_queue.put(status)
                break
        if not queue.empty():
            image = queue.get()
            disp_arr[:] = image
            pygame.display.flip()
    print("Finished rendering")
    return

def main():
    queue = mp.Queue()
    command_queue = mp.Queue()
    display = pygame.display.set_mode((N, N))

    p_refresh = mp.Process(target=refresh_image, args=(queue, command_queue))
    p_show = mp.Process(target=show_image, args=(queue, command_queue, display))
    # Deixem córrer el procés
    p_refresh.start()
    p_show.start()
    #p_status.start()
    while True:
        status = input("> ")
        command_queue.put(status)
        if status == "stop":
            # Buida la cua
            while not queue.empty():
                queue.get()
            command_queue.close()
            queue.close()
            break

    p_show.join()
    p_refresh.join()

    pygame.display.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
