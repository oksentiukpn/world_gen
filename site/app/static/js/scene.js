import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls;
let planetMesh;
let baseVertices = null;
let targetPositions = null;
let currentPositions = null;
let targetColors = null;
let currentColors = null;
let currentRadius = 10;
const TERRAIN_DISPLACEMENT_SCALE = 0.02;

export function initScene() {
  const container = document.getElementById('canvas-container');

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a1a); // Dark space background

  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 0, 30);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
  dirLight.position.set(5, 3, 5);
  scene.add(dirLight);

  const backLight = new THREE.DirectionalLight(0x4444ff, 0.3);
  backLight.position.set(-5, -3, -5);
  scene.add(backLight);

  window.addEventListener('resize', onWindowResize);

  animate();
}

function onWindowResize() {
  const container = document.getElementById('canvas-container');
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

export function initBaseMesh(verticesBuffer, facesBuffer, radius) {
  currentRadius = radius;

  // The Python backend sends vertices as np.float32 and faces as np.int32
  const vArray32 = new Float32Array(verticesBuffer);
  const fArray32 = new Uint32Array(facesBuffer); // Three.js requires Uint16 or Uint32 for indices

  const vCount = vArray32.length / 3;

  baseVertices = new Float32Array(vCount * 3);
  currentPositions = new Float32Array(vCount * 3);
  targetPositions = new Float32Array(vCount * 3);

  currentColors = new Float32Array(vCount * 3);
  targetColors = new Float32Array(vCount * 3);

  for (let i = 0; i < vArray32.length; i += 3) {
    const x = vArray32[i];
    const y = vArray32[i + 1];
    const z = vArray32[i + 2];

    const len = Math.sqrt(x * x + y * y + z * z);
    const nx = len > 0 ? x / len : 0;
    const ny = len > 0 ? y / len : 0;
    const nz = len > 0 ? z / len : 0;

    baseVertices[i] = nx;
    baseVertices[i + 1] = ny;
    baseVertices[i + 2] = nz;

    const px = nx * radius;
    const py = ny * radius;
    const pz = nz * radius;

    currentPositions[i] = px;
    currentPositions[i + 1] = py;
    currentPositions[i + 2] = pz;

    targetPositions[i] = px;
    targetPositions[i + 1] = py;
    targetPositions[i + 2] = pz;

    // Default color: gray
    currentColors[i] = 0.5;
    currentColors[i + 1] = 0.5;
    currentColors[i + 2] = 0.5;
    targetColors[i] = 0.5;
    targetColors[i + 1] = 0.5;
    targetColors[i + 2] = 0.5;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(currentPositions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(currentColors, 3));
  geometry.setIndex(new THREE.BufferAttribute(fArray32, 1));
  geometry.computeVertexNormals();

  const material = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.8,
    metalness: 0.1,
    flatShading: false
  });

  if (planetMesh) {
    scene.remove(planetMesh);
    planetMesh.geometry.dispose();
    planetMesh.material.dispose();
  }

  planetMesh = new THREE.Mesh(geometry, material);
  scene.add(planetMesh);

  // Adjust camera distance based on radius
  camera.position.set(0, 0, radius * 3);
}

export function updateHeights(heightmapBuffer) {
  if (!baseVertices) return;

  // Python heightmap is np.float32
  const hArray32 = new Float32Array(heightmapBuffer);

  for (let i = 0; i < hArray32.length; i++) {
    const h = hArray32[i];

    const idx = i * 3;
    const nx = baseVertices[idx];
    const ny = baseVertices[idx + 1];
    const nz = baseVertices[idx + 2];

    const finalRadius = currentRadius + h * TERRAIN_DISPLACEMENT_SCALE;

    targetPositions[idx] = nx * finalRadius;
    targetPositions[idx + 1] = ny * finalRadius;
    targetPositions[idx + 2] = nz * finalRadius;
  }
}

export function updateColors(biomeMapBuffer) {
  if (!currentColors) return;

  // Python biome_map is np.uint8
  const colorsUint8 = new Uint8Array(biomeMapBuffer);

  for (let i = 0; i < colorsUint8.length; i++) {
    targetColors[i] = colorsUint8[i] / 255.0;
  }
}

function animate() {
  requestAnimationFrame(animate);

  controls.update();

  // Lerp positions and colors
  if (planetMesh && targetPositions && currentPositions) {
    let needsUpdate = false;

    for (let i = 0; i < currentPositions.length; i++) {
      // Lerp position
      const diffP = targetPositions[i] - currentPositions[i];
      if (Math.abs(diffP) > 0.001) {
        currentPositions[i] += diffP * 0.1;
        needsUpdate = true;
      } else {
        currentPositions[i] = targetPositions[i];
      }

      // Lerp color
      const diffC = targetColors[i] - currentColors[i];
      if (Math.abs(diffC) > 0.001) {
        currentColors[i] += diffC * 0.1;
        needsUpdate = true;
      } else {
        currentColors[i] = targetColors[i];
      }
    }

    if (needsUpdate) {
      planetMesh.geometry.attributes.position.needsUpdate = true;
      planetMesh.geometry.attributes.color.needsUpdate = true;
      planetMesh.geometry.computeVertexNormals();
    }

    planetMesh.rotation.y += 0.001; // Slow spin
  }

  renderer.render(scene, camera);
}
