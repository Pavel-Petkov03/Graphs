import pygame
import math


class Vertex:
    def __init__(self, color, radius, position):
        self.color = color
        self.radius = radius
        self.position = position

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def check_collision(self, other_circle):
        distance = math.sqrt((self.position[0] - other_circle.position[0]) ** 2 +
                             (self.position[1] - other_circle.position[1]) ** 2)
        return distance <= (self.radius + other_circle.radius)


class State:
    pass


class VertexState:
    default_state = ""

    def __init__(self):
        self.current_state = VertexState.default_state


class EdgeState:
    def __init__(self):
        self.start = True


class Edge:
    def __init__(self, vertex_one, vertex_two):
        self.vertex_one = vertex_one
        self.vertex_two = vertex_two

    def draw(self, screen):
        pygame.draw.line(screen, "green", self.vertex_one.position, self.vertex_two.position)


class Button(pygame.Rect):
    def __init__(self, width, height, x, y, text, state, text_color="black"):
        super().__init__(x, y, width, height)
        self.color = "yellow"
        self.text = text
        self.text_color = text_color
        self.state = state

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self, 0)
        self.draw_text_center(screen)

    def draw_text_center(self, screen):
        max_font_size = int(self.height * 0.2)
        font = pygame.font.Font(None, max_font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.center)
        screen.blit(text_surface, text_rect)


class ScreenPart(pygame.Rect):
    def __init__(self, rect, parent):
        super().__init__(rect)
        self.parent = parent

    def draw(self, screen):
        pygame.draw.rect(screen, "gray", self)


class UpperMenu(ScreenPart):
    def __init__(self, rect, parent):
        super().__init__(rect, parent)

        self.buttons = [Button(100, 100, 0, 0, "vertex", VertexState()), Button(100, 100, 100, 0, "edges", EdgeState())]
        self.rect = 0

    def draw(self, screen):
        pygame.draw.rect(screen, "gray", self)
        for button in self.buttons:
            button.draw(screen)

    def button_collide(self, pos):
        for button in self.buttons:
            if button.collidepoint(*pos):
                return button


class VertexSideMenu:
    pass


class SideMenu(ScreenPart):
    def __init__(self, rect, parent):
        super().__init__(rect, parent)

    def draw(self, screen):
        pygame.draw.rect(screen, "green", self)

    def write(self):
        current_state = self.parent.state
        if isinstance(current_state, VertexState):
            pass


class Board(ScreenPart):
    DEFAULT_VERTEX_COLOR = "blue"
    VERTEX_COLOR_IN_EDGE_MOD = "red"

    def __init__(self, rect, parent):
        super().__init__(rect, parent)
        self.vertices = []
        self.edges = []
        self.current_edge = Edge(None, None)

    def draw(self, screen):
        pygame.draw.rect(screen, "black", self)
        for edge in self.edges:
            edge.draw(screen)
        for vertex in self.vertices:
            vertex.draw(screen)

    def append_vertex(self, pos):
        if self.collides_with_menus(pos):
            return
        current_vertex = Vertex("purple", 12.5, pos)
        if not self.vertex_collides(current_vertex):
            self.vertices.append(current_vertex)
            return

    def collides_with_menus(self, pos):
        return self.parent.side_menu.collidepoint(pos) or self.parent.upper_menu.collidepoint(pos)

    def vertex_collides(self, current_vertex):
        for vertex in self.vertices:
            if vertex.check_collision(current_vertex):
                return vertex
        return False

    def color_vertices(self, color):
        for vertex in self.vertices:
            vertex.color = color

    def append_edge(self, pos):
        if self.collides_with_menus(pos):
            return
        approximate_vertex = Vertex("yellow", 12.5, pos)
        current_vertex = self.vertex_collides(approximate_vertex)
        if self.parent.state.start:
            self.color_vertices(Board.VERTEX_COLOR_IN_EDGE_MOD)
            self.parent.state.start = False
            if current_vertex:
                self.current_edge.vertex_one = current_vertex
                current_vertex.color = "yellow"
        else:
            if not current_vertex:
                return
            if self.current_edge.vertex_one is None:
                self.current_edge.vertex_one = current_vertex
                current_vertex.color = "yellow"
                return
            self.current_edge.vertex_two = current_vertex
            self.edges.append(self.current_edge)
            self.current_edge = Edge(None, None)
            self.parent.state.start = True
            self.color_vertices(Board.DEFAULT_VERTEX_COLOR)


class ScreenUI:
    DEFAULT_STATE = VertexState()

    def __init__(self):
        self.side_menu = SideMenu(pygame.Rect((1440 - 300, 0), (300, 900)), self)
        self.upper_menu = UpperMenu(pygame.Rect((0, 0), (1440, 100)), self)
        self.board = Board(pygame.Rect((0, 100), (1440 - 300, 900 - 100)), self)
        self.state = ScreenUI.DEFAULT_STATE

    def draw(self, screen):
        self.side_menu.draw(screen)
        self.upper_menu.draw(screen)
        self.board.draw(screen)

    def dispatch_click_event(self, pos):
        collide_button = self.upper_menu.button_collide(pos)
        if collide_button:
            self.state = collide_button.state
            collide_button.color = "red"
            return

        if isinstance(self.state, VertexState):
            self.board.append_vertex(pos)
        elif isinstance(self.state, EdgeState):
            self.board.append_edge(pos)


class Engine:
    def __init__(self):
        pygame.init()
        self.screen = self.create_screen()
        self.ui = ScreenUI()
        self.fps = 60
        pygame.display.set_caption("Circle Component")

    @staticmethod
    def create_screen():
        screen_width = 1366
        screen_height = 768
        screen = pygame.display.set_mode((screen_width, screen_height))
        return screen

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    self.ui.dispatch_click_event(pos)

            self.ui.draw(self.screen)
            pygame.display.flip()
            pygame.time.Clock().tick(self.fps)

        pygame.quit()


if __name__ == "__main__":
    engine = Engine()
    engine.run()
