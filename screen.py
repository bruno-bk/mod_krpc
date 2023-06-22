class Screen:
    def __init__(self, connection):
        self.connection = connection
        self.panel = None
        self.size_of_screen = [500, 300]
        self.font_size = 18
        self.line_size = [self.size_of_screen[0], self.font_size + 4]
        self.elements = {}
        self.telemetry = {}
        self.buttons = {}
        self.creat_screen()
        self.lines_of_telemetry = 0
        self.lines_of_input = 0

    def creat_screen(self):
        canvas = self.connection.ui.stock_canvas
        screen_size = canvas.rect_transform.size

        self.panel = canvas.add_panel()
        self.panel.rect_transform.size = self.size_of_screen
        self.panel.rect_transform.position = (260-(screen_size[0]/2), (screen_size[1]/2)-200)

    def add_button(self, name, creat_stream, size, position):
        button_launch = self.panel.add_button(name)
        button_launch.rect_transform.position = position
        button_launch.rect_transform.size = size
        if creat_stream == True:
            self.buttons[name] = [button_launch, self.connection.add_stream(getattr, button_launch, 'clicked')]
        else:
            self.buttons[name] = [button_launch]

    def get_state_of_button(self, name):
        result = False
        if(len(self.buttons[name]) == 2):
            result = self.buttons[name][1]()
            if result == True:
                self.buttons[name][1] = False
        else:
            # TODO - log warn
            print("stream não criada")

        return result

    def add_status_of_launch(self, name):
        text_status = self.panel.add_text("")
        text_status.rect_transform.position = (-80, -125)
        text_status.rect_transform.size = (320, 50)
        text_status.color = (1, 1, 1)
        text_status.size = self.font_size
        self.elements[name] = text_status

    def update_value_of_element(self, element, value):
        self.elements[element].content = value

    def add_telemetry(self, name, unit, stream):
        self.lines_of_telemetry += 1
        element = self.panel.add_text(name + ": 0 " + unit)
        element.rect_transform.position = (-120, 150-(self.lines_of_telemetry*self.line_size[1]))
        element.rect_transform.size = (240, self.line_size[1])
        element.color = (1, 1, 1)
        element.size = self.font_size
        self.telemetry[name] = [element, stream, unit]

    def update_telemetry(self):
        for i in self.telemetry:
            self.telemetry[i][0].content = "{}: {:.2f} {}".format(i, self.telemetry[i][1](), self.telemetry[i][2])
