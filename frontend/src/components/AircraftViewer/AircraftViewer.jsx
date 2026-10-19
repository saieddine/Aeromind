import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'

function AircraftModel() {
  const { scene } = useGLTF('/models/a320/a320.glb')

  scene.traverse((object) => {
    console.log(object.name, object.type)
  })

  return (
    <primitive
      object={scene}
      scale={0.1}
      position={[0.3, -0.28, 0]}
    />
  )
}

function AircraftViewer() {
  return (
    <Canvas camera={{ position: [5, 3, 6], fov: 45 }}>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} intensity={2} />

      <AircraftModel />

      <OrbitControls />
    </Canvas>
  )
}

export default AircraftViewer