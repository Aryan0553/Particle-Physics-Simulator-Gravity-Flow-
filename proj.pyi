import tkinter as tk
import random
import math
import time

class Particle:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        
        # Generate a random bright color in hex format
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        self.color = f'#{r:02x}{g:02x}{b:02x}'
        
        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # Physics properties
        self.gravity = 0.1
        self.bounce = 0.8  # Energy retained after bounce
        self.friction = 0.99  # Air friction
        
        # Lifespan and age
        self.max_life = random.randint(50, 150)
        self.age = 0
        
        # Create the oval shape on the canvas
        self.shape = canvas.create_oval(
            x - self.size, y - self.size,
            x + self.size, y + self.size,
            fill=self.color, outline=""
        )
    
    def update(self, width, height, gravity_points):
        # Update age
        self.age += 1
        
        # Apply gravity
        self.vy += self.gravity
        
        # Apply forces from gravity points
        for gx, gy, _ in gravity_points:
            # Calculate distance to gravity point
            dx = gx - self.x
            dy = gy - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
            
            # Apply force (inversely proportional to distance)
            force = 40 / (distance * distance)  # Adjust strength
            angle = math.atan2(dy, dx)
            
            self.vx += math.cos(angle) * force
            self.vy += math.sin(angle) * force
        
        # Apply friction
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Handle collisions with walls
        if self.x - self.size < 0:  # Left wall
            self.x = self.size
            self.vx = -self.vx * self.bounce
        elif self.x + self.size > width:  # Right wall
            self.x = width - self.size
            self.vx = -self.vx * self.bounce
            
        if self.y - self.size < 0:  # Top wall
            self.y = self.size
            self.vy = -self.vy * self.bounce
        elif self.y + self.size > height:  # Bottom wall
            self.y = height - self.size
            self.vy = -self.vy * self.bounce
        
        # Move the shape on the canvas
        self.canvas.coords(
            self.shape,
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size
        )
        
        # Fade out based on age
        if self.age > self.max_life / 2:
            remaining_life = self.max_life - self.age
            alpha = remaining_life / (self.max_life / 2)
            
            # Make the particle more transparent by mixing with background color (black)
            r = int(int(self.color[1:3], 16) * alpha)
            g = int(int(self.color[3:5], 16) * alpha)
            b = int(int(self.color[5:7], 16) * alpha)
            faded_color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.itemconfig(self.shape, fill=faded_color)
        
        # Return True if the particle is still alive
        if self.age >= self.max_life:
            self.canvas.delete(self.shape)
            return False
        return True


class ParticleSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Particle Physics Simulation")
        
        # Set window dimensions
        self.width = 800
        self.height = 600
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Particle system
        self.particles = []
        self.gravity_points = []
        self.spawn_rate = 5
        
        # Add initial particles
        for _ in range(50):
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            self.add_particles(x, y)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
        # Bind keyboard events
        self.root.bind("c", self.clear_particles)
        self.root.bind("g", self.clear_gravity_points)
        self.root.bind("h", self.toggle_help)
        
        # Help text
        self.show_help = True
        self.help_text = self.canvas.create_text(
            10, 10, anchor=tk.NW, fill='white', font=('Arial', 10),
            text="Left-click: Create particles\nRight-click: Create gravity point\n" +
                 "H: Toggle help text\nC: Clear particles\nG: Clear gravity points"
        )
        
        # Start animation
        self.update()
    
    def add_particles(self, x, y, count=1):
        for _ in range(count):
            particle = Particle(self.canvas, x, y)
            self.particles.append(particle)
    
    def add_gravity_point(self, x, y):
        # Create visual indicator for gravity point
        circle = self.canvas.create_oval(x-8, y-8, x+8, y+8, outline='white')
        outer_circle = self.canvas.create_oval(x-40, y-40, x+40, y+40, outline='#6666FF')
        
        self.gravity_points.append((x, y, (circle, outer_circle)))
        
        # Limit number of gravity points
        if len(self.gravity_points) > 3:
            old_x, old_y, (old_circle, old_outer) = self.gravity_points.pop(0)
            self.canvas.delete(old_circle)
            self.canvas.delete(old_outer)
    
    def on_left_click(self, event):
        self.add_particles(event.x, event.y, self.spawn_rate)
    
    def on_right_click(self, event):
        self.add_gravity_point(event.x, event.y)
    
    def clear_particles(self, event=None):
        for particle in self.particles:
            self.canvas.delete(particle.shape)
        self.particles = []
    
    def clear_gravity_points(self, event=None):
        for _, _, (circle, outer_circle) in self.gravity_points:
            self.canvas.delete(circle)
            self.canvas.delete(outer_circle)
        self.gravity_points = []
    
    def toggle_help(self, event=None):
        self.show_help = not self.show_help
        if self.show_help:
            self.canvas.itemconfig(self.help_text, state=tk.NORMAL)
        else:
            self.canvas.itemconfig(self.help_text, state=tk.HIDDEN)
    
    def update(self):
        start_time = time.time()
        
        # Update particle count display
        particle_count_text = f"Particles: {len(self.particles)}"
        self.canvas.delete("particle_count")
        self.canvas.create_text(
            10, 70, anchor=tk.NW, fill='white', font=('Arial', 10),
            text=particle_count_text, tags="particle_count"
        )
        
        # Update all particles
        new_particles = []
        for particle in self.particles:
            if particle.update(self.width, self.height, self.gravity_points):
                new_particles.append(particle)
        self.particles = new_particles
        
        # Calculate time taken for the update
        elapsed = time.time() - start_time
        delay = max(1, int(16.67 - elapsed * 1000))  # Target ~60 FPS
        
        # Schedule the next update
        self.root.after(delay, self.update)


def main():
    root = tk.Tk()
    app = ParticleSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()