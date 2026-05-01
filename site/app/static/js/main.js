import { initScene, initBaseMesh, updateHeights, updateColors } from './scene.js';

let socket;

document.addEventListener('DOMContentLoaded', () => {
  // Initialize 3D Scene
  initScene();

  // Initialize Socket.IO connection
  socket = io();

  const generateBtn = document.getElementById('generateBtn');
  const statusText = document.getElementById('statusText');
  const seedInput = document.getElementById('seed');
  const radiusInput = document.getElementById('radius');
  const radiusNumInput = document.getElementById('radiusNum');
  const subdivisionsInput = document.getElementById('subdivisions');
  const noiseScaleInput = document.getElementById('noise_scale');
  const octavesInput = document.getElementById('octaves');
  const persistenceInput = document.getElementById('persistence');
  const lacunarityInput = document.getElementById('lacunarity');
  const amplitudeInput = document.getElementById('amplitude');
  const water_levelInput = document.getElementById('water_level');
  const sharpnessStrengthInput = document.getElementById('sharpness_strength');

  // Sync radius slider and number input
  radiusInput.addEventListener('input', (e) => {
    radiusNumInput.value = e.target.value;
  });

  radiusNumInput.addEventListener('input', (e) => {
    radiusInput.value = e.target.value;
  });

  generateBtn.addEventListener('click', () => {
    const config = {
      seed: parseInt(seedInput.value) || 42,
      radius: parseFloat(radiusNumInput.value) || 10,
      subdivisions: parseInt(subdivisionsInput.value) || 4,
      noise_scale: parseFloat(noiseScaleInput.value) || 1,
      octaves: parseInt(octavesInput.value) || 4,
      persistence: parseFloat(persistenceInput.value) || 0.4,
      lacunarity: parseFloat(lacunarityInput.value) || 2,
      amplitude: parseFloat(amplitudeInput.value) || 1,
      water_level: parseFloat(water_levelInput.value) || 0.375,
      sharpness_strength: parseFloat(sharpnessStrengthInput.value) || 1
    };

    generateBtn.disabled = true;
    generateBtn.classList.add('opacity-50', 'cursor-not-allowed');
    statusText.textContent = "Connecting to generator...";
    statusText.classList.add('animate-pulse', 'text-yellow-400');
    statusText.classList.remove('text-green-400', 'text-red-400');

    socket.emit('generate_planet', config);
  });

  socket.on('step_progress', (data) => {
    statusText.textContent = `[Step ${data.step}/4]: ${data.message}`;
  });

  socket.on('step_base', (data) => {
    // data.vertices and data.faces are ArrayBuffers
    initBaseMesh(data.vertices, data.faces, data.radius);
  });

  socket.on('step_noise', (data) => {
    updateHeights(data.heightmap);
  });

  socket.on('step_noise_refined', (data) => {
    updateHeights(data.heightmap);
  });

  socket.on('step_biome', (data) => {
    updateColors(data.biome_map);
  });

  socket.on('generation_complete', (data) => {
    statusText.textContent = "Generation complete!";
    statusText.classList.remove('animate-pulse', 'text-yellow-400');
    statusText.classList.add('text-green-400');

    generateBtn.disabled = false;
    generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
  });

  socket.on('generation_error', (data) => {
    statusText.textContent = `Error: ${data.message}`;
    statusText.classList.remove('animate-pulse', 'text-yellow-400');
    statusText.classList.add('text-red-400');

    generateBtn.disabled = false;
    generateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    console.error(data.message);
  });
});
