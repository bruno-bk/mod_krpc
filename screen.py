class Screen:
    def __init__(self, connection):
        self.connection = connection
        self.panel = None
        self.size_of_screen = [500, 300]
        self.font_size = 18
        self.input_size = [120, 30]
        self.line_size = [self.size_of_screen[0], self.font_size + 4]
        self.texts = {}
        self.buttons = {}
        self.inputs = {}
        self.lines_of_telemetry = 0
        self.lines_of_input = 0

    def creat_screen(self, size, position):
        if self.panel != None:
            self.clear_screen()

        canvas = self.connection.ui.stock_canvas
        self.panel = canvas.add_panel()
        self.panel.rect_transform.size = size
        self.panel.rect_transform.position = position
    
    def clear_screen(self):
        self.connection.ui.clear()
        self.texts.clear()
        self.buttons.clear()
        self.inputs.clear()

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
                self.buttons[name][0].clicked = False
        else:
            # TODO - log warn
            print("stream não criada")

        return result

    def add_status_of_launch(self, name):
        self.texts[name] = [self.create_text_element([320, 50], [-80, -125])]

    def update_text_value(self, element, value):
        self.texts[element][0].content = value

    def add_telemetry(self, name, unit, stream):
        self.lines_of_telemetry += 1
        element = self.create_text_element([240, self.line_size[1]], [-120, 150-(self.lines_of_telemetry*self.line_size[1])])
        self.texts[name] = [element, stream, unit]
        self.update_telemetry()

    def create_text_element(self, size, position):
        element = self.panel.add_text("")
        element.rect_transform.position = position
        element.rect_transform.size = size
        element.color = (1, 1, 1)
        element.size = self.font_size
        return element

    def update_telemetry(self):
        for i in self.texts:
            if(len(self.texts[i]) == 3):
                self.update_text_value(i, "{}: {:.2f} {}".format(i, self.texts[i][1](), self.texts[i][2]))

    def add_input(self, name, value, min, max):
        self.lines_of_input += 1
        input = self.panel.add_input_field()
        input.value = str(value)
        input.rect_transform.position = [180, 150-(self.lines_of_input*self.input_size[1])]
        input.rect_transform.size = self.input_size

        label = self.create_text_element([120, self.input_size[1]], [70, 150-(self.lines_of_input*self.input_size[1])])
        label.content = name + ":"

        self.inputs[name] = [label, input, min, max]

    def get_input_value(self, name):
        if self.inputs[name][2] != None and self.inputs[name][3] != None:
            if int(self.inputs[name][1].value) < int(self.inputs[name][2]):
                self.inputs[name][1].value = str(self.inputs[name][2])

            if int(self.inputs[name][1].value) > int(self.inputs[name][3]):
                self.inputs[name][1].value = str(self.inputs[name][3])

        return self.inputs[name][1].value
