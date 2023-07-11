import krpc
import time

from screen import Screen
import orbit_launch

def connect_to_server():
    conn = None
    try:
        conn = krpc.connect(name='rocket controller')
    except:
        print("Falha ao se conectar, verifique se o servidor esta online em 127.0.0.1")
    return conn

def minimized_screen(screen):
    screen.creat_screen([80, 30], [500, -520])

    screen.add_button("x", True, [20, 20], [25, 0])
    screen.add_button("o", True, [20, 20], [ 3, 0])
    while 1:
        if screen.get_state_of_button("x"):
            exit()

        if screen.get_state_of_button("o"):
            return

        time.sleep(.1)

def menu_screnn(conn, screen):
    screen_size = conn.ui.stock_canvas.rect_transform.size
    screen.creat_screen([150, 190], (260-(screen_size[0]/2), (screen_size[1]/2)-200))

    screen.add_button("x", True, [20,20], [60, 82])
    screen.add_button("_", True, [20,20], [38, 82])

    button_size = [140, 40]
    amount_of_buttons = 0

    screen.add_button("Orbit launch", True, button_size, [0, 50-(button_size[1] * amount_of_buttons)])
    amount_of_buttons += 1
    screen.add_button("in development 1...", False, button_size, [0, 50-(button_size[1] * amount_of_buttons)])
    amount_of_buttons += 1
    screen.add_button("in development 2...", False, button_size, [0, 50-(button_size[1] * amount_of_buttons)])
    amount_of_buttons += 1
    screen.add_button("in development 3...", False, button_size, [0, 50-(button_size[1] * amount_of_buttons)])
    amount_of_buttons += 1

    while 1:
        try:
            if screen.get_state_of_button("Orbit launch"):
                orbit_launch.launch(conn, screen)
                return

            if screen.get_state_of_button("x"):
                exit()

            if screen.get_state_of_button("_"):
                minimized_screen(screen)
                return

            time.sleep(.1)
        except Exception as Argument:
            print(f"Error: {Argument}")
            return

def main():
    conn = None
    while conn == None:
        conn = connect_to_server()
        time.sleep(1)

    screen = Screen(conn)
    while(1):
        menu_screnn(conn, screen)

main()
