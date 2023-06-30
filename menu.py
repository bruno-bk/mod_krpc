import krpc
import time

from screen import Screen

def connect_to_server():
    conn = None
    try:
        conn = krpc.connect(name='rocket controller')
    except:
        print("Falha ao se conectar, verifique se o servidor esta online em 127.0.0.1")
    return conn

def main():
    conn = None
    while conn == None:
        conn = connect_to_server()
        time.sleep(1)

    screen = Screen(conn)
    screen_size = conn.ui.stock_canvas.rect_transform.size
    screen.creat_screen([150, 190], (260-(screen_size[0]/2), (screen_size[1]/2)-200))

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
        if screen.get_state_of_button("Orbit launch"):
            print("Orbit launch")

        time.sleep(.1)

main()