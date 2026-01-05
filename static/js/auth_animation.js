/**
 * Constellation Animation for Auth Pages
 * Renders a moving network of nodes and connections on a canvas.
 */
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];

    // Configuration
    const PARTICLE_COUNT = 80; // Number of dots
    const LINK_DISTANCE = 150; // Max distance to draw a line
    const SPEED = 0.5; // Movement speed

    // Resize handling
    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resize);
    resize();

    // Particle Class
    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * SPEED;
            this.vy = (Math.random() - 0.5) * SPEED;
            this.size = Math.random() * 2 + 1; // Size between 1 and 3
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Bounce off edges
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(59, 130, 246, 0.6)'; // Blue-ish dots
            ctx.fill();
        }
    }

    // Initialize Particles
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }

    // Animation Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Update and Draw Particles
        particles.forEach(p => {
            p.update();
            p.draw();
        });

        // Draw Connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < LINK_DISTANCE) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(59, 130, 246, ${1 - distance / LINK_DISTANCE})`; // Fade out with distance
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
});
