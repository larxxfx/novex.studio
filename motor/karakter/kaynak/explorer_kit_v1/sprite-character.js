/**
 * NØVEX Sprite Character Engine
 * Lightweight canvas renderer for transparent PNG frame sequences.
 */
export class SpriteCharacter {
  constructor({ canvas, manifest, x = 0.5, y = 0.92, height = 0.62 }) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.manifest = manifest;
    this.x = x;
    this.y = y;
    this.height = height;
    this.animation = "idle";
    this.frameIndex = 0;
    this.elapsed = 0;
    this.lastTime = 0;
    this.images = {};
    this.loaded = false;
    this.loadPromise = this.loadAssets();
    this.raf = 0;
  }

  async loadAssets() {
    const entries = Object.entries(this.manifest.animations);
    await Promise.all(entries.flatMap(([name, anim]) =>
      anim.frames.map((src, i) => new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          (this.images[name] ||= [])[i] = img;
          resolve();
        };
        img.onerror = reject;
        img.src = new URL(src, document.baseURI).href;
      }))
    ));
    this.loaded = true;
  }

  setAnimation(name, { restart = false } = {}) {
    if (!this.manifest.animations[name]) throw new Error(`Unknown animation: ${name}`);
    if (this.animation !== name || restart) {
      this.animation = name;
      this.frameIndex = 0;
      this.elapsed = 0;
    }
  }

  setPosition(x, y) { this.x = x; this.y = y; }
  setHeight(normalizedHeight) { this.height = normalizedHeight; }

  draw() {
    if (!this.loaded) return;
    const ctx = this.ctx;
    const canvas = this.canvas;
    const anim = this.manifest.animations[this.animation];
    const img = this.images[this.animation]?.[this.frameIndex];
    if (!img) return;

    const targetH = canvas.height * this.height;
    const scale = targetH / img.height;
    const w = img.width * scale;
    const h = img.height * scale;
    const dx = canvas.width * this.x - w / 2;
    const dy = canvas.height * this.y - h;

    ctx.drawImage(img, dx, dy, w, h);
  }

  start() {
    const tick = (now) => {
      const dt = this.lastTime ? (now - this.lastTime) / 1000 : 0;
      this.lastTime = now;
      const anim = this.manifest.animations[this.animation];
      this.elapsed += dt;
      const frameDuration = 1 / (anim.fps || 8);
      while (this.elapsed >= frameDuration) {
        this.elapsed -= frameDuration;
        if (this.frameIndex < anim.frames.length - 1) {
          this.frameIndex++;
        } else if (anim.loop) {
          this.frameIndex = 0;
        }
      }
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.draw();
      this.raf = requestAnimationFrame(tick);
    };
    this.raf = requestAnimationFrame(tick);
  }

  stop() {
    cancelAnimationFrame(this.raf);
    this.raf = 0;
  }
}
