import pygame
import random
import math
import neat
import os
import pickle

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_VELOCITY = 5
GRAVITY = 0.5
JUMP_STRENGTH = -10
TIME_COUNTER = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.radius = 20
        self.color = YELLOW
        self.alive = True
        self.score = 0
        self.fitness = 0
        
    def jump(self):
        if self.alive:
            self.velocity = JUMP_STRENGTH
            
    def update(self):
        if self.alive:
            # Apply gravity
            self.velocity += GRAVITY
            self.y += self.velocity
            
            # Check bounds
            if self.y <= 0 or self.y >= SCREEN_HEIGHT - GROUND_HEIGHT:
                self.alive = False
                
    def draw(self, screen):
        if self.alive:
            # Draw bird with rotation based on velocity
            angle = min(max(self.velocity * 3, -45), 45)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            # Draw a simple beak
            pygame.draw.polygon(screen, (255, 165, 0), [
                (self.x + self.radius, self.y),
                (self.x + self.radius + 10, self.y - 5),
                (self.x + self.radius + 10, self.y + 5)
            ])
            
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

def get_current_gap_size():
    """Calculate the current gap size based on time"""
    global TIME_COUNTER
    
    # Start reducing gap after 500 frames (about 8 seconds at 60 FPS)
    if TIME_COUNTER < 500:
        return PIPE_GAP
    else:
        # Reduce gap by 2 pixels every 200 frames after 500
        reduction_cycles = (TIME_COUNTER - 500) // 200
        reduction_amount = reduction_cycles * 2
        # Minimum gap of 100 to keep it challenging but possible
        current_gap = max(100, PIPE_GAP - reduction_amount)
        return current_gap

class Pipe:
    def __init__(self, x):
        self.x = x
        
        # Use the global gap calculation function
        current_gap = get_current_gap_size()
        
        # Ensure gap fits within screen bounds
        min_top = 50
        max_bottom_start = SCREEN_HEIGHT - GROUND_HEIGHT - current_gap - 50
        
        self.gap_y = random.randint(min_top, max_bottom_start)
        self.top_height = self.gap_y
        self.bottom_y = self.gap_y + current_gap
        self.bottom_height = SCREEN_HEIGHT - GROUND_HEIGHT - self.bottom_y
        self.passed = False
        
        # Store the gap size for this pipe (for display purposes)
        self.gap_size = current_gap
        
    def update(self):
        self.x -= PIPE_VELOCITY
        
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.top_height))
        pygame.draw.rect(screen, BLACK, (self.x, 0, PIPE_WIDTH, self.top_height), 2)
        
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height))
        pygame.draw.rect(screen, BLACK, (self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height), 2)
        
        # Draw gap size indicator on the pipe (for debugging)
        if self.x > 50 and self.x < SCREEN_WIDTH - 100:  # Only show for visible pipes
            font = pygame.font.Font(None, 24)
            gap_text = font.render(str(self.gap_size), True, BLACK)
            text_rect = gap_text.get_rect(center=(self.x + PIPE_WIDTH//2, self.gap_y + self.gap_size//2))
            screen.blit(gap_text, text_rect)
        
    def collides_with(self, bird):
        bird_rect = bird.get_rect()
        top_pipe_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top_height)
        bottom_pipe_rect = pygame.Rect(self.x, self.bottom_y, PIPE_WIDTH, self.bottom_height)
        
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)
        
    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird NEAT - Progressive Difficulty")
        self.clock = pygame.time.Clock()
        self.birds = []
        self.pipes = []
        self.pipe_timer = 0
        self.generation = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def add_bird(self, bird):
        self.birds.append(bird)
        
    def reset(self):
        global TIME_COUNTER
        self.birds = []
        self.pipes = []
        self.pipe_timer = 0
        TIME_COUNTER = 0  # Reset time counter when game resets
        
    def get_next_pipe(self, bird):
        """Get the next pipe that the bird needs to navigate"""
        for pipe in self.pipes:
            if pipe.x + PIPE_WIDTH > bird.x:
                return pipe
        return None
        
    def get_inputs(self, bird):
        """Get neural network inputs for a bird"""
        inputs = []
        
        # Bird's y position (normalized)
        inputs.append(bird.y / SCREEN_HEIGHT)
        
        # Bird's velocity (normalized)
        inputs.append(bird.velocity / 15)
        
        next_pipe = self.get_next_pipe(bird)
        if next_pipe:
            # Distance to next pipe (normalized)
            inputs.append((next_pipe.x - bird.x) / SCREEN_WIDTH)
            
            # Top pipe height (normalized)
            inputs.append(next_pipe.top_height / SCREEN_HEIGHT)
            
            # Bottom pipe y position (normalized)
            inputs.append(next_pipe.bottom_y / SCREEN_HEIGHT)
        else:
            # No pipe ahead
            inputs.extend([1.0, 0.5, 0.5])
            
        return inputs
        
    def update(self, nets=None, genomes=None):
        global TIME_COUNTER
        # Update pipe timer and add new pipes
        self.pipe_timer += 1
        TIME_COUNTER += 1
        
        # Add pipe every 90 frames
        if self.pipe_timer > 90:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            self.pipe_timer = 0
            
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
                
        # Update birds
        if nets and genomes:
            # NEAT mode - use neural networks
            for i, bird in enumerate(self.birds[:]):
                if bird.alive:
                    # Get neural network inputs
                    inputs = self.get_inputs(bird)
                    
                    # Get neural network output
                    output = nets[i].activate(inputs)
                    
                    # Decide whether to jump
                    if output[0] > 0.5:
                        bird.jump()
                        
                    bird.update()
                    
                    # Update fitness (distance traveled)
                    genomes[i][1].fitness += 2
                    
                    # Reward for staying in the middle 50% of the screen (25-75 percentile)
                    middle_zone_min = SCREEN_HEIGHT * 0.25
                    middle_zone_max = SCREEN_HEIGHT * 0.75
                    if middle_zone_min <= bird.y <= middle_zone_max:
                        genomes[i][1].fitness += 1
                    
                    # Check pipe collisions and scoring
                    for pipe in self.pipes:
                        if pipe.collides_with(bird):
                            bird.alive = False
                            
                        # Check if bird passed pipe
                        if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                            pipe.passed = True
                            bird.score += 1
                            genomes[i][1].fitness += 100  # Bonus for passing pipe
                            
                    if not bird.alive:
                        self.birds.remove(bird)
        else:
            # Manual mode - keyboard controls
            for bird in self.birds[:]:
                if bird.alive:
                    bird.update()
                    
                    # Check collisions
                    for pipe in self.pipes:
                        if pipe.collides_with(bird):
                            bird.alive = False
                            
                        if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                            pipe.passed = True
                            bird.score += 1
                            
    def draw(self):
        # Clear screen with sky color
        self.screen.fill(BLUE)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw ground
        pygame.draw.rect(self.screen, BROWN, 
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Draw birds
        for bird in self.birds:
            bird.draw(self.screen)
            
        # Draw UI
        if self.birds:
            score_text = self.font.render(f"Score: {max(bird.score for bird in self.birds)}", 
                                        True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
        alive_text = self.font.render(f"Birds Alive: {len([b for b in self.birds if b.alive])}", 
                                    True, BLACK)
        self.screen.blit(alive_text, (10, 50))
        
        gen_text = self.font.render(f"Generation: {self.generation}", True, BLACK)
        self.screen.blit(gen_text, (10, 90))
        
        # Display current difficulty info
        current_gap = get_current_gap_size()
        time_seconds = TIME_COUNTER // 60  # Convert frames to seconds (assuming 60 FPS)
        
        difficulty_text = self.font.render(f"Gap Size: {current_gap}px", True, BLACK)
        self.screen.blit(difficulty_text, (10, 130))
        
        timer_text = self.font.render(f"Time: {time_seconds}s (Frame: {TIME_COUNTER})", True, BLACK)
        self.screen.blit(timer_text, (10, 170))
        
        # Show difficulty progression info
        if TIME_COUNTER < 500:
            next_reduction = 500 - TIME_COUNTER
            info_text = self.small_font.render(f"Difficulty increases in {next_reduction // 60}s", True, BLACK)
            self.screen.blit(info_text, (10, 210))
        else:
            cycles_completed = (TIME_COUNTER - 500) // 200
            frames_to_next = 200 - ((TIME_COUNTER - 500) % 200)
            next_gap = max(100, PIPE_GAP - (cycles_completed + 1) * 2)
            info_text = self.small_font.render(f"Next reduction to {next_gap}px in {frames_to_next // 60}s", True, BLACK)
            self.screen.blit(info_text, (10, 210))
        
        pygame.display.flip()
        
    def run_manual(self):
        """Run game in manual mode for testing"""
        self.reset()
        self.add_bird(Bird(100, SCREEN_HEIGHT // 2))
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in self.birds:
                            if bird.alive:
                                bird.jump()
                    elif event.key == pygame.K_r:
                        # Reset game
                        self.reset()
                        self.add_bird(Bird(100, SCREEN_HEIGHT // 2))
                                
            self.update()
            self.draw()
            self.clock.tick(60)
            
            # Check if all birds are dead
            if not any(bird.alive for bird in self.birds):
                print(f"Game Over! Final Score: {max(bird.score for bird in self.birds)} | Time Survived: {TIME_COUNTER // 60}s | Final Gap: {get_current_gap_size()}px")
                # Auto restart after 3 seconds
                pygame.time.wait(3000)
                self.reset()
                self.add_bird(Bird(100, SCREEN_HEIGHT // 2))
                
        pygame.quit()


def run_neat(config_path, headless=True):
    """Run NEAT algorithm"""
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                               neat.DefaultSpeciesSet, neat.DefaultStagnation,
                               config_path)
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    def eval_genomes(genomes, config):
        game = Game()
        game.generation = population.generation
        
        nets = []
        ge = []
        birds = []
        
        # Create birds and networks for each genome
        for genome_id, genome in genomes:
            genome.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            birds.append(Bird(100, SCREEN_HEIGHT // 2))
            ge.append((genome_id, genome))
            
        game.birds = birds
        
        # Run simulation
        frame_count = 0
        max_frames = 5000  # Increased to allow for longer gameplay with progressive difficulty
        
        while len(game.birds) > 0 and frame_count < max_frames:
            # Only handle quit events if not headless
            if not headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                        
            game.update(nets, ge)
            
            # Only draw if not headless
            if not headless:
                game.draw()
                game.clock.tick(60)
            
            frame_count += 1
            
        # Print generation summary
        if game.birds:
            max_score = max(bird.score for bird in game.birds if hasattr(bird, 'score'))
            final_gap = get_current_gap_size()
            print(f"Generation {game.generation}: Max Score: {max_score}, Final Gap: {final_gap}px, Time: {TIME_COUNTER // 60}s")
            
    # Run NEAT for 200 generations
    winner = population.run(eval_genomes, 200)
    print(f"Best genome: {winner}")
    
    # Get the top 20 genomes from the final generation
    final_genomes = list(population.population.values())
    # Filter out genomes with None fitness and ensure all have valid fitness values
    valid_genomes = [g for g in final_genomes if g.fitness is not None]
    # If we don't have enough valid genomes, use all available
    if len(valid_genomes) < 20:
        # Set fitness to 0 for genomes with None fitness
        for g in final_genomes:
            if g.fitness is None:
                g.fitness = 0
        valid_genomes = final_genomes
    
    # Sort by fitness (descending)
    valid_genomes.sort(key=lambda g: g.fitness, reverse=True)
    top_20_genomes = valid_genomes[:20]
    
    # Save the winner (best genome)
    with open("best_bird.pkl", "wb") as f:
        pickle.dump(winner, f)
    print("Winner saved to best_bird.pkl")
    
    # Save the top 20 genomes for demo
    with open("top_20_birds.pkl", "wb") as f:
        pickle.dump(top_20_genomes, f)
    print(f"Top {len(top_20_genomes)} birds saved to top_20_birds.pkl")
    
    return winner

def demo_best_bird(config_path):
    """Demo the top 20 trained birds"""
    # Try to load the top 20 genomes first
    top_genomes = []
    try:
        with open("epic_bird.pkl", "rb") as f:
            top_genomes = pickle.load(f)
        print(f"Loaded {len(top_genomes)} top birds from top_20_birds.pkl")
    except FileNotFoundError:
        # Fallback to single best bird
        try:
            with open("epic_bird.pkl", "rb") as f:
                winner = pickle.load(f)
            top_genomes = [winner]
            print("Loaded best bird from best_bird.pkl")
        except FileNotFoundError:
            print("No trained birds found! Run training first with: python flappy_bird.py train")
            return
    
    # Load config and create networks
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                               neat.DefaultSpeciesSet, neat.DefaultStagnation,
                               config_path)
    
    networks = []
    for genome in top_genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
    
    # Create game
    game = Game()
    
    print(f"Watching {len(top_genomes)} top birds play with progressive difficulty!")
    print("Controls: ESC=Quit, R=Restart")
    print("Bird colors: Red=Best, Orange=Top 5, Yellow=Top 10, Green=Others")
    print("Gap starts at 200px and reduces by 2px every 3.3 seconds after 8 seconds")
    
    def reset_game():
        game.reset()
        birds = []
        for i in range(len(networks)):
            bird = Bird(100, SCREEN_HEIGHT // 2)
            # Give each bird a slightly different color for identification
            if i == 0:
                bird.color = (255, 0, 0)  # Red for the best bird
            elif i < 5:
                bird.color = (255, 165, 0)  # Orange for top 5
            elif i < 10:
                bird.color = (255, 255, 0)  # Yellow for top 10
            else:
                bird.color = (0, 255, 0)  # Green for the rest
            birds.append(bird)
            game.add_bird(bird)
        return birds
    
    birds = reset_game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    birds = reset_game()
                    
        # Update all alive birds
        alive_birds = [bird for bird in birds if bird.alive]
        
        if alive_birds:
            for i, bird in enumerate(birds):
                if bird.alive and i < len(networks):
                    # Get neural network inputs
                    inputs = game.get_inputs(bird)
                    
                    # Get neural network output
                    output = networks[i].activate(inputs)
                    
                    # Decide whether to jump
                    if output[0] > 0.5:
                        bird.jump()
                        
                    bird.update()
                    
                    # Check pipe collisions and scoring
                    for pipe in game.pipes:
                        if pipe.collides_with(bird):
                            bird.alive = False
                            
                        if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                            pipe.passed = True
                            bird.score += 1
            
            # Update pipes using the main game update
            game.pipe_timer += 1
            if game.pipe_timer > 90:
                game.pipes.append(Pipe(SCREEN_WIDTH))
                game.pipe_timer = 0
                
            # Update TIME_COUNTER
            global TIME_COUNTER
            TIME_COUNTER += 1
                
            for pipe in game.pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    game.pipes.remove(pipe)
            
            game.draw()
            game.clock.tick(60)
        else:
            # All birds are dead, show final scores
            if birds:
                scores = [bird.score for bird in birds]
                best_score = max(scores)
                avg_score = sum(scores) / len(scores)
                final_gap = get_current_gap_size()
                survival_time = TIME_COUNTER // 60
                print(f"All birds died! Best: {best_score}, Avg: {avg_score:.1f}, Time: {survival_time}s, Final Gap: {final_gap}px")
            
            # Auto-restart after 3 seconds
            pygame.time.wait(3000)
            birds = reset_game()
            
    pygame.quit()

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "neat_config.txt")
    
    # Check command line arguments
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "train":
            print("Starting NEAT training for 200 generations (headless mode)...")
            run_neat(config_path, headless=True)
        elif sys.argv[1] == "train-visual":
            print("Starting NEAT training for 200 generations (visual mode)...")
            run_neat(config_path, headless=False)
        elif sys.argv[1] == "demo":
            demo_best_bird(config_path)
        elif sys.argv[1] == "manual":
            game = Game()
            game.run_manual()
        else:
            print("Usage:")
            print("  python flappy_bird.py train        - Train fast (no graphics)")
            print("  python flappy_bird.py train-visual - Train with graphics")
            print("  python flappy_bird.py demo         - Watch the top 20 birds play")
            print("  python flappy_bird.py manual       - Play manually")
    else:
        # Default behavior - check if we have a trained bird
        if os.path.exists("best_bird.pkl") or os.path.exists("top_20_birds.pkl"):
            print("Found trained bird! Starting demo...")
            demo_best_bird(config_path)
        else:
            print("No trained bird found. Starting fast training...")
            run_neat(config_path, headless=True)
            print("\nTraining complete! Starting demo...")
            demo_best_bird(config_path)