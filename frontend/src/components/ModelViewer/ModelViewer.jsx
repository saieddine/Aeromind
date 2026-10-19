import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'

function Model({ modelPath, scale = 1 }) {
  const { scene } = useGLTF(modelPath)

  return (
    <primitive
      object={scene}
      scale={scale}
      position={[0, -0.5, 0]}
    />
  )
}

function ModelViewer({ modelPath, scale = 1 }) {
  return (
    <Canvas camera={{ position: [4, 3, 5], fov: 45 }}>
      <ambientLight intensity={1.5} />
      <directionalLight
        position={[5, 5, 5]}
        intensity={2}
      />

      <Suspense fallback={null}>
        <Model modelPath={modelPath} scale={scale} />
      </Suspense>

      <OrbitControls makeDefault />
    </Canvas>
  )
}

export default ModelViewer

