# AeroMind ✈️

### Interactive Aircraft Exploration Platform

AeroMind is a web-based project that brings aircraft information, technical specifications, and interactive 3D visualization together in one interface. The project currently focuses on the Airbus A320 family, with a dedicated viewer for the CFM56-5B engine.

The goal is to make aircraft exploration more interactive and accessible through a modern web interface.

## Features

- **Aircraft selection:** Browse aircraft manufacturers and available aircraft options.
- **Airbus A320:** Explore aircraft information and technical specifications.
- **Interactive 3D viewer:** Rotate and inspect aircraft models directly in the browser.
- **Engine exploration:** View the CFM56-5B engine in a separate interactive 3D window.
- **Technical exploration interface:** A foundation for presenting aircraft systems and components.
- **Aerospace-inspired UI:** A dark interface with blue accents, technical details, and interactive components.

Some features, including the Boeing interface and additional aircraft systems, are still under development.

## Technologies Used

| Technology | Purpose |
|---|---|
| React | Building the user interface |
| Vite | Development server and build tooling |
| JavaScript | Application logic |
| CSS | Layout, styling, and animations |
| Three.js | 3D graphics rendering |
| React Three Fiber | Using Three.js within React |
| React Three Drei | 3D helpers and camera controls |

## Project Structure

```text
AeroMind/
├── public/
│   └── models/
│       ├── a320/
│       │   └── a320.glb
│       └── engine/
│           └── cfm56-5b.glb
├── src/
│   ├── components/
│   │   ├── AircraftViewer/
│   │   └── ModelViewer/
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── CREDITS.md
├── index.html
├── package.json
└── README.md
```

*The structure above is illustrative; component and asset locations may vary slightly depending on the current project files.*

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (which includes npm)
- Git
- A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/Nirmin-Z/AeroMind.git
```

### 2. Navigate to the project

```bash
cd AeroMind
```

### 3. Install dependencies

```bash
npm install
```

### 4. Start the development server

```bash
npm run dev
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:5173
```

### 5. Create a production build

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

## 3D Assets and Licensing

AeroMind uses third-party 3D models for aircraft and engine visualization. These assets are subject to their respective licenses and attribution requirements.

- **Airbus A320-200:** Sourced from the [amvlab/aircraft-models repository](https://github.com/amvlab/aircraft-models).
- **CFM56-5B engine:** Sourced from [Sketchfab](https://sketchfab.com/3d-models/cfm56-5b-6958dfcec16e453b989efe014ab00d64).

See [CREDITS.md](./CREDITS.md) for creator attribution, original asset links, and license information.

## Current Status

AeroMind is under development. The current version focuses on the frontend, aircraft selection, aircraft specifications, and interactive 3D model viewing.

Future improvements may include:

- Additional aircraft and engine models
- More detailed aircraft systems
- Expanded technical information
- AI-assisted aircraft information and exploration

## Acknowledgements

Thanks to the creators who share 3D models under licenses that allow reuse and adaptation. Their work supports the development of AeroMind.

# AeroMind ✈️

### Interactive Aircraft Exploration Platform

AeroMind is a web-based project that brings aircraft information, technical specifications, and interactive 3D visualization together in one interface. The project currently focuses on the Airbus A320 family, with a dedicated viewer for the CFM56-5B engine.

The goal is to make aircraft exploration more interactive and accessible through a modern web interface.

## Features

- **Aircraft selection:** Browse aircraft manufacturers and available aircraft options.
- **Airbus A320:** Explore aircraft information and technical specifications.
- **Interactive 3D viewer:** Rotate and inspect aircraft models directly in the browser.
- **Engine exploration:** View the CFM56-5B engine in a separate interactive 3D window.
- **Technical exploration interface:** A foundation for presenting aircraft systems and components.
- **Aerospace-inspired UI:** A dark interface with blue accents, technical details, and interactive components.

Some features, including the Boeing interface and additional aircraft systems, are still under development.

## Technologies Used

| Technology | Purpose |
|---|---|
| React | Building the user interface |
| Vite | Development server and build tooling |
| JavaScript | Application logic |
| CSS | Layout, styling, and animations |
| Three.js | 3D graphics rendering |
| React Three Fiber | Using Three.js within React |
| React Three Drei | 3D helpers and camera controls |

## Project Structure

```text
AeroMind/
├── public/
│   └── models/
│       ├── a320/
│       │   └── a320.glb
│       └── engine/
│           └── cfm56-5b.glb
├── src/
│   ├── components/
│   │   ├── AircraftViewer/
│   │   └── ModelViewer/
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── CREDITS.md
├── index.html
├── package.json
└── README.md
```

*The structure above is illustrative; component and asset locations may vary slightly depending on the current project files.*

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (which includes npm)
- Git
- A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/Nirmin-Z/AeroMind.git
```

### 2. Navigate to the project

```bash
cd AeroMind
```

### 3. Install dependencies

```bash
npm install
```

### 4. Start the development server

```bash
npm run dev
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:5173
```

### 5. Create a production build

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

## 3D Assets and Licensing

AeroMind uses third-party 3D models for aircraft and engine visualization. These assets are subject to their respective licenses and attribution requirements.

- **Airbus A320-200:** Sourced from the [amvlab/aircraft-models repository](https://github.com/amvlab/aircraft-models).
- **CFM56-5B engine:** Sourced from [Sketchfab](https://sketchfab.com/3d-models/cfm56-5b-6958dfcec16e453b989efe014ab00d64).

See [CREDITS.md](./CREDITS.md) for creator attribution, original asset links, and license information.

## Current Status

AeroMind is under development. The current version focuses on the frontend, aircraft selection, aircraft specifications, and interactive 3D model viewing.

Future improvements may include:

- Additional aircraft and engine models
- More detailed aircraft systems
- Expanded technical information
- AI-assisted aircraft information and exploration

## Acknowledgements

Thanks to the creators who share 3D models under licenses that allow reuse and adaptation. Their work supports the development of AeroMind.

## Author

The FrontEnd is developed by [Nirmin-Z](https://github.com/Nirmin-Z).