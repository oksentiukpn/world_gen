import { initScene, initBaseMesh, updateHeights, updateColors } from './scene.js';

let socket;

document.addEventListener('DOMContentLoaded', () => {
  // Initialize 3D Scene
  initScene();

  // Initialize Socket.IO connection
  socket = io();

  const generateBtn = document.getElementById('generateBtn');
  const statusText = document.getElementById('statusText');
  const statusIndicator = document.getElementById('statusIndicator');

  const seedInput = document.getElementById('seed');
  const randomSeedBtn = document.getElementById('randomSeedBtn');

  // UI Toggles
  const advancedToggle = document.getElementById('advancedToggle');
  const advancedContent = document.getElementById('advancedContent');
  const advancedIcon = document.getElementById('advancedIcon');

  advancedToggle.addEventListener('click', () => {
    advancedContent.classList.toggle('hidden');
    advancedContent.classList.toggle('flex');
    if (advancedContent.classList.contains('hidden')) {
      advancedIcon.classList.remove('rotate-180');
    } else {
      advancedIcon.classList.add('rotate-180');
    }
  });

  randomSeedBtn.addEventListener('click', () => {
    seedInput.value = Math.floor(Math.random() * 1000000);
    // Optional: Add a small animation to the button
    randomSeedBtn.querySelector('svg').classList.add('animate-spin');
    setTimeout(() => randomSeedBtn.querySelector('svg').classList.remove('animate-spin'), 500);
  });

  // Sliders and Labels
  const radiusInput = document.getElementById('radius');
  const radiusNumInput = document.getElementById('radiusNum');
  const radiusLabel = document.getElementById('radiusLabel');

  const subdivisionsInput = document.getElementById('subdivisions');
  const subdivisionsNumInput = document.getElementById('subdivisionsNum');
  const subLabel = document.getElementById('subLabel');

  const noiseScaleInput = document.getElementById('noise_scale');
  const octavesInput = document.getElementById('octaves');
  const persistenceInput = document.getElementById('persistence');
  const lacunarityInput = document.getElementById('lacunarity');
  const amplitudeInput = document.getElementById('amplitude');
  const water_levelInput = document.getElementById('water_level');
  const sharpnessStrengthInput = document.getElementById('sharpness_strength');
  const plateIterationsInput = document.getElementById('plate_iterations');
  const plateCountInput = document.getElementById('plate_count');
  const rangeRadiusInput = document.getElementById('range_radius');
  const rangeAmplitudeInput = document.getElementById('range_amplitude');


  // Sync sliders
  radiusInput.addEventListener('input', (e) => {
    radiusNumInput.value = e.target.value;
    radiusLabel.textContent = e.target.value;
  });

  subdivisionsInput.addEventListener('input', (e) => {
    subdivisionsNumInput.value = e.target.value;
    subLabel.textContent = e.target.value;
  });

  function updateStatus(message, state = 'ready') {
    statusText.textContent = message;
    statusIndicator.className = 'w-2 h-2 rounded-full'; // reset

    if (state === 'working') {
      statusIndicator.classList.add('bg-yellow-400', 'animate-pulse', 'shadow-[0_0_8px_rgba(250,204,21,0.8)]');
    } else if (state === 'error') {
      statusIndicator.classList.add('bg-red-500', 'shadow-[0_0_8px_rgba(239,68,68,0.8)]');
    } else {
      statusIndicator.classList.add('bg-green-500', 'shadow-[0_0_8px_rgba(34,197,94,0.8)]');
    }
  }

  generateBtn.addEventListener('click', () => {
    const config = {
      seed: parseInt(seedInput.value) || 42,
      radius: parseFloat(radiusNumInput.value) || 10,
      subdivisions: parseInt(subdivisionsNumInput.value) || 4,
      noise_scale: parseFloat(noiseScaleInput.value) || 1,
      octaves: parseInt(octavesInput.value) || 4,
      persistence: parseFloat(persistenceInput.value) || 0.4,
      lacunarity: parseFloat(lacunarityInput.value) || 2,
      amplitude: parseFloat(amplitudeInput.value) || 1,
      water_level: parseFloat(water_levelInput.value) || 0.375,
      sharpness_strength: parseFloat(sharpnessStrengthInput.value) || 1,
      plate_iterations: parseInt(plateIterationsInput.value) || 1,
      plate_count: parseInt(plateCountInput.value) || 1,
      range_radius: parseFloat(rangeRadiusInput.value) || 1,
      range_amplitude: parseFloat(rangeAmplitudeInput.value) || 1,
    };

    generateBtn.disabled = true;
    generateBtn.querySelector('span').innerHTML = `
      <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
      Generating...
    `;
    generateBtn.classList.add('opacity-75', 'cursor-not-allowed');
    updateStatus("Connecting to generator...", "working");

    socket.emit('generate_planet', config);
  });

  socket.on('step_progress', (data) => {
    updateStatus(`[Step ${data.step}/4]: ${data.message}`, "working");
  });

  socket.on('step_base', (data) => {
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
    updateStatus("Generation complete!", "ready");

    generateBtn.disabled = false;
    generateBtn.querySelector('span').innerHTML = `
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      Generate World
    `;
    generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
  });

  socket.on('generation_error', (data) => {
    updateStatus(`Error: ${data.message}`, "error");

    generateBtn.disabled = false;
    generateBtn.querySelector('span').innerHTML = `
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      Retry Generation
    `;
    generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    console.error(data.message);
  });
});
