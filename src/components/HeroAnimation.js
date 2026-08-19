import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * A component that renders a swirling cloud of particles.
 */
const DataCloud = ({ count = 5000 }) => {
    const pointsRef = useRef();

    // Generate random points within a sphere shape, memoized for performance.
    const particles = useMemo(() => {
        const temp = [];
        const radius = 2.5;
        for (let i = 0; i < count; i++) {
            const r = radius * Math.cbrt(Math.random()); // Distribute points more evenly within the sphere
            const theta = Math.random() * 2 * Math.PI;
            const phi = Math.acos(2 * Math.random() - 1);
            const x = r * Math.sin(phi) * Math.cos(theta);
            const y = r * Math.sin(phi) * Math.sin(theta);
            const z = r * Math.cos(phi);
            temp.push(x, y, z);
        }
        return new Float32Array(temp);
    }, [count]);

    // Animate the cloud on every frame
    useFrame((state, delta) => {
        if (pointsRef.current) {
            pointsRef.current.rotation.y += delta * 0.05;
            pointsRef.current.rotation.x += delta * 0.02;
        }
    });

    return (
        <points ref={pointsRef}>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" count={particles.length / 3} array={particles} itemSize={3} />
            </bufferGeometry>
            <pointsMaterial size={0.02} color="#00A896" sizeAttenuation transparent opacity={0.7} />
        </points>
    );
};

/**
 * A utility component to animate the camera based on mouse position.
 */
const CameraAnimator = () => {
    useFrame((state) => {
        // Gently move the camera based on the pointer's position for a parallax effect
        state.camera.position.lerp(new THREE.Vector3(state.pointer.x * 1.5, state.pointer.y * 1.5, 5), 0.03);
        state.camera.lookAt(0, 0, 0);
    });
    return null;
};

const HeroAnimation = () => (
    <div className="hero-canvas-container">
        <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <DataCloud />
            <CameraAnimator />
        </Canvas>
    </div>
);

export default HeroAnimation;