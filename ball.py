import matplotlib.pyplot as plt
import matplotlib.animation as animation
from av import VideoFrame
from PIL import Image

# Acceleration due to gravity, m.s-2.
g = 9.81
# The maximum x-range of ball's trajectory to plot.
XMAX = 5
# The coefficient of restitution for bounces (-v_up/v_down).
cor = 0.65
# The time step for the animation.
dt = 0.05

# Initial position and velocity vectors.
x0, y0 = 0, 4
vx0, vy0 = 1, 0

class Ball():
    def __init__(self):
        # Acceleration due to gravity, m.s-2.
        self.g = 20
        # The maximum x-range of ball's trajectory to plot.
        self.XMAX = 500
        # The coefficient of restitution for bounces (-v_up/v_down).
        self.cor = 0.65
        # The time step for the animation.
        self.dt = 0.07

        # Initial position and velocity vectors.
        self.x0, self.y0 = 0, 4
        self.vx0, self.vy0 = 1, 0
        self.t = 0
    
    def get_pos(self, t=0):
        """A generator yielding the ball's position at time t."""
        x, y, vx, vy = self.x0, self.y0, self.vx0, self.vy0
        while x < XMAX:
            t += self.dt
            x += vx0 * self.dt
            y += vy * self.dt
            vy -= g * self.dt
            if y < 0:
                # bounce when y < 0
                y = 0
                vy = -vy * cor # reverse vy direction and reduce vy by a fraction
            yield x, y
    
    def draw_image(self, x, y):
        #draw a matplotlib figure according current ball position, save it to temp.png
        fig, ax = plt.subplots()
        ax.set_aspect('equal')

        line, = ax.plot([x], [y], lw=2, marker="o", markersize=5, markerfacecolor="blue")
        plt.xlim([-1, 5])
        plt.ylim([0, 5])
        plt.savefig("temp.png")
        plt.close()
    
    def generate_frames(self):
        #generate VideoFrames
        gen = self.get_pos()
        count = 1
        frames = []
        while count <= 50:
            x, y = next(gen)
            self.draw_image(x, y)
            img = Image.open("temp.png")
            frame = VideoFrame.from_image(img) #convert from png to VideoFrame
            count += 1
            frames.append(frame)
        return frames

