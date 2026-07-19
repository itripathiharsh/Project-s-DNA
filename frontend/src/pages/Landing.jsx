import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Box, Sphere, MeshDistortMaterial, Line } from '@react-three/drei';
import Lenis from 'lenis';
import * as THREE from 'three';
import { Terminal, Network, BrainCircuit, ShieldAlert, Cpu, ChevronRight, Mail } from 'lucide-react';

// -----------------------------------------------------------------------------
// 1. Smooth Scrolling Wrapper (Lenis)
// -----------------------------------------------------------------------------
const SmoothScroll = ({ children }) => {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      smooth: true,
    });
    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
    return () => lenis.destroy();
  }, []);
  return <>{children}</>;
};

// -----------------------------------------------------------------------------
// 2. DNA Helix 3D Component
// -----------------------------------------------------------------------------
const DNAHelix = () => {
  const groupRef = useRef();
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.3;
      groupRef.current.position.y = Math.sin(t * 0.5) * 0.5;
    }
  });

  const numPairs = 15;
  const radius = 1.5;
  const height = 8;
  const pairs = useMemo(() => {
    const arr = [];
    for (let i = 0; i < numPairs; i++) {
      const y = (i / numPairs - 0.5) * height;
      const angle = i * 0.5;
      arr.push({ id: i, y, angle });
    }
    return arr;
  }, [numPairs]);

  return (
    <group ref={groupRef} position={[0, 0, 0]} scale={1.2}>
      {pairs.map((p) => (
        <group key={p.id} position={[0, p.y, 0]} rotation={[0, p.angle, 0]}>
          <Sphere args={[0.25, 32, 32]} position={[-radius, 0, 0]}>
            <MeshDistortMaterial color="#9d4edd" emissive="#5a189a" emissiveIntensity={0.8} distort={0.3} speed={2} />
          </Sphere>
          <Sphere args={[0.25, 32, 32]} position={[radius, 0, 0]}>
            <MeshDistortMaterial color="#00f5d4" emissive="#00bbf9" emissiveIntensity={0.8} distort={0.3} speed={2} />
          </Sphere>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.02, 0.02, radius * 2]} />
            <meshStandardMaterial color="#333" transparent opacity={0.5} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

// -----------------------------------------------------------------------------
// 3. Code City 3D Component
// -----------------------------------------------------------------------------
const CodeCity = () => {
  const cityRef = useRef();
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (cityRef.current) {
      cityRef.current.rotation.y = t * 0.05;
    }
  });

  const buildings = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 80; i++) {
      const x = (Math.random() - 0.5) * 30;
      const z = (Math.random() - 0.5) * 30;
      const h = Math.random() * 8 + 1;
      const isHotspot = Math.random() > 0.9;
      const color = isHotspot ? '#ff0055' : Math.random() > 0.5 ? '#9d4edd' : '#00f5d4';
      arr.push({ x, z, h, color, isHotspot });
    }
    return arr;
  }, []);

  return (
    <group ref={cityRef}>
      {buildings.map((b, i) => (
        <Box key={i} args={[0.8, b.h, 0.8]} position={[b.x, b.h / 2 - 4, b.z]}>
          <meshStandardMaterial 
            color={b.color} 
            emissive={b.color} 
            emissiveIntensity={b.isHotspot ? 1 : 0.2} 
            wireframe={!b.isHotspot && Math.random() > 0.7} 
          />
        </Box>
      ))}
      <gridHelper args={[40, 40, '#222', '#111']} position={[0, -4, 0]} />
    </group>
  );
};

// -----------------------------------------------------------------------------
// 4. Knowledge Graph 3D Component
// -----------------------------------------------------------------------------
const NodeGraph3D = () => {
  const groupRef = useRef();
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.1;
      groupRef.current.rotation.x = Math.sin(t * 0.05) * 0.2;
    }
  });

  const nodes = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 20; i++) {
      arr.push(new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      ));
    }
    return arr;
  }, []);

  const lines = useMemo(() => {
    const arr = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].distanceTo(nodes[j]) < 4.5) {
          arr.push([nodes[i], nodes[j]]);
        }
      }
    }
    return arr;
  }, [nodes]);

  return (
    <group ref={groupRef}>
      {nodes.map((pos, i) => (
        <Sphere key={i} args={[0.15, 16, 16]} position={pos}>
          <meshStandardMaterial color={i === 0 ? "#ff0055" : "#00f5d4"} emissive={i === 0 ? "#ff0055" : "#00f5d4"} emissiveIntensity={0.8} />
        </Sphere>
      ))}
      {lines.map((pts, i) => (
        <Line key={i} points={pts} color="#444" lineWidth={1} transparent opacity={0.3} />
      ))}
    </group>
  );
};

// -----------------------------------------------------------------------------
// 5. Hero Section (Split Layout)
// -----------------------------------------------------------------------------
const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen w-full flex items-center bg-[#000] overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/20 blur-[120px] rounded-full pointer-events-none opacity-50" />
      
      <div className="max-w-7xl mx-auto px-6 w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10 pt-20">
        
        {/* Left: Typography */}
        <div className="flex flex-col items-start text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-gray-300 text-xs font-semibold tracking-widest uppercase mb-8 backdrop-blur-md"
          >
            <span className="w-2 h-2 rounded-full bg-signal-cyan animate-pulse" />
            Project DNA Engine
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
            className="text-6xl lg:text-7xl xl:text-8xl font-black text-white tracking-tighter leading-[1.1] mb-6"
          >
            Understand <br/>
            Software. <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-300 to-gray-600">
              Completely.
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
            className="text-lg text-gray-400 max-w-lg mb-10 leading-relaxed font-light"
          >
            Transform any repository into a living, interactive knowledge graph. 
            Discover architectural flaws, mitigate risks, and let the AI guide your next refactor.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.3 }}
            className="flex flex-wrap items-center gap-4"
          >
            <button
              onClick={() => navigate('/onboarding')}
              className="group flex items-center gap-2 px-8 py-4 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-all duration-300"
            >
              Analyze Repository
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => document.getElementById('pipeline').scrollIntoView({ behavior: 'smooth' })}
              className="px-8 py-4 bg-transparent border border-white/20 text-white font-semibold rounded-full hover:bg-white/5 transition-all duration-300"
            >
              Explore Features
            </button>
          </motion.div>
        </div>

        {/* Right: 3D Canvas */}
        <div className="h-[60vh] lg:h-[90vh] w-full relative">
          <Canvas camera={{ position: [0, 0, 8], fov: 40 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={2} />
            <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
              <DNAHelix />
            </Float>
          </Canvas>
        </div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 6. Bento Grid Features (The DNA Pipeline)
// -----------------------------------------------------------------------------
const PipelineSection = () => {
  return (
    <section id="pipeline" className="py-32 px-6 bg-[#000] relative">
      <div className="max-w-7xl mx-auto">
        
        <div className="mb-20">
          <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
            The DNA Pipeline
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl font-light">
            From raw source code to a fully queryable, AI-driven knowledge base in seconds. 
            A unified engine for architectural intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]">
          
          {/* Bento Box 1: Knowledge Graph (Large) */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="md:col-span-2 md:row-span-2 rounded-3xl bg-[#0a0a0a] border border-white/10 p-8 relative overflow-hidden group hover:border-white/20 transition-colors"
          >
            <div className="absolute inset-0 z-0 opacity-40 group-hover:opacity-80 transition-opacity duration-700">
              <Canvas camera={{ position: [0, 0, 12], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <NodeGraph3D />
              </Canvas>
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/50 to-transparent z-10" />
            <div className="relative z-20 h-full flex flex-col justify-end">
              <Network className="w-10 h-10 text-signal-cyan mb-4" />
              <h3 className="text-3xl font-bold text-white mb-2">Semantic Knowledge Graph</h3>
              <p className="text-gray-400 max-w-md leading-relaxed">
                We parse your codebase into a multi-dimensional graph. Every function, class, and module is mapped, revealing hidden dependencies and architectural coupling.
              </p>
            </div>
          </motion.div>

          {/* Bento Box 2: AST Parsing */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-3xl bg-[#0a0a0a] border border-white/10 p-8 flex flex-col justify-between group hover:border-white/20 transition-colors"
          >
            <Cpu className="w-8 h-8 text-signal-rose mb-4" />
            <div>
              <h3 className="text-xl font-bold text-white mb-2">AST Parsing</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Deep structural analysis of your source code. We extract entities without executing code, keeping it safe and blazing fast.
              </p>
            </div>
          </motion.div>

          {/* Bento Box 3: AI Intelligence */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-3xl bg-gradient-to-br from-[#0a0a0a] to-primary/10 border border-white/10 p-8 flex flex-col justify-between group hover:border-primary/30 transition-colors"
          >
            <BrainCircuit className="w-8 h-8 text-primary mb-4" />
            <div>
              <h3 className="text-xl font-bold text-white mb-2">AI Intelligence</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Evidence-backed reasoning. Our AI doesn't hallucinate; it reads the graph to give you deterministic, exact refactoring steps.
              </p>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 7. Interactive Code City Section
// -----------------------------------------------------------------------------
const CodeCitySection = () => {
  return (
    <section className="h-[90vh] w-full relative bg-[#000] border-y border-white/10 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [15, 12, 15], fov: 45 }}>
          <ambientLight intensity={0.2} />
          <directionalLight position={[10, 20, 10]} intensity={1.5} color="#fff" />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.3} maxPolarAngle={Math.PI / 2.2} />
          <CodeCity />
        </Canvas>
      </div>
      
      {/* Vignette Overlays */}
      <div className="absolute inset-0 z-10 pointer-events-none bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-[#000]/40 to-[#000]" />
      
      <div className="absolute bottom-16 left-6 md:left-16 z-20 max-w-lg pointer-events-none">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="p-8 rounded-3xl bg-black/60 border border-white/10 backdrop-blur-md"
        >
          <div className="flex items-center gap-3 mb-4">
            <ShieldAlert className="w-6 h-6 text-signal-rose" />
            <h2 className="text-2xl font-bold text-white">Visual Hotspots</h2>
          </div>
          <p className="text-gray-400 leading-relaxed font-light">
            Code City renders your folders as districts and files as buildings. Height represents complexity. Glowing red structures highlight high-churn, high-risk code that demands immediate attention.
          </p>
        </motion.div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 8. Live Terminal / Features Section
// -----------------------------------------------------------------------------
const TerminalSection = () => {
  const [text, setText] = useState('');
  const fullText = `> Executing Project DNA Engine...
> Extracting AST from 1,204 files... [DONE 0.4s]
> Mapping dependency graph... [DONE 0.2s]
> Detecting circular references... [FOUND 3]
> Analyzing security hotspots... [FOUND 1]
> Compiling metrics... [DONE]
> 
> SYSTEM READY.
> Awaiting intelligence queries...`;

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setText(fullText.substring(0, i));
      i++;
      if (i > fullText.length) clearInterval(interval);
    }, 15);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-32 px-6 bg-[#000] relative overflow-hidden">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-20 items-center">
        
        <div className="flex-1 space-y-8">
          <h2 className="text-4xl md:text-6xl font-black text-white leading-tight tracking-tight">
            Real-time <br className="hidden md:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-cyan to-signal-blue pb-2 block">Intelligence</span>
          </h2>
          <p className="text-lg text-gray-400 font-light max-w-md">
            The engine builds a deterministic semantic graph of your entire architecture. 
            Ask complex questions, simulate refactoring impacts, and generate production-ready documentation instantly.
          </p>
          
          <ul className="space-y-5">
            {[
              'Predictive Analytics & Forecasting', 
              'Automated Refactoring Suite', 
              'Security & Risk Heatmaps', 
              'Semantic Repository Search'
            ].map((feature, i) => (
              <motion.li 
                key={i} 
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="flex items-center gap-4 text-gray-300 font-medium"
              >
                <div className="w-6 h-6 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                  <div className="w-2 h-2 rounded-full bg-white" />
                </div>
                {feature}
              </motion.li>
            ))}
          </ul>
        </div>

        <div className="flex-1 w-full relative">
          {/* Glow behind terminal */}
          <div className="absolute inset-0 bg-signal-cyan/20 blur-[100px] rounded-full pointer-events-none" />
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#0a0a0a] relative z-10"
          >
            <div className="flex items-center px-4 py-4 bg-[#111] border-b border-white/5 gap-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
              <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
              <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
              <div className="ml-4 text-xs text-gray-500 font-mono tracking-widest uppercase">dna-engine ~ bash</div>
            </div>
            <div className="p-6 font-mono text-sm text-signal-cyan min-h-[300px] leading-relaxed whitespace-pre-wrap selection:bg-signal-cyan/30">
              {text}
              <span className="animate-pulse">_</span>
            </div>
          </motion.div>
        </div>

      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 9. Footer / Final CTA Section
// -----------------------------------------------------------------------------
const CTAFooter = () => {
  const navigate = useNavigate();
  return (
    <footer className="relative flex flex-col items-center justify-center overflow-hidden bg-[#000] border-t border-white/10 pt-32 pb-12 px-6">
      <div className="absolute inset-0 z-0 opacity-30 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 15] }}>
          <ambientLight intensity={0.5} />
          <Float speed={2} floatIntensity={2}>
            <DNAHelix />
          </Float>
        </Canvas>
      </div>
      
      <div className="absolute inset-0 bg-gradient-to-t from-[#000] via-[#000]/80 to-transparent z-10 pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-20 text-center max-w-2xl mb-32"
      >
        <h2 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">Ready to Decode?</h2>
        <p className="text-xl text-gray-400 mb-10 font-light">Stop guessing. Start understanding. The future of software intelligence is here.</p>
        
        <button
          onClick={() => navigate('/onboarding')}
          className="group inline-flex items-center gap-2 px-10 py-5 bg-white text-black font-bold text-lg rounded-full hover:scale-105 transition-all duration-300 shadow-[0_0_40px_rgba(255,255,255,0.2)]"
        >
          Initialize Workspace
          <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </motion.div>

      {/* Credits */}
      <div className="relative z-20 flex flex-col items-center gap-4 text-gray-500 text-sm">
        <div className="flex items-center gap-6 mb-2">
          <a href="https://github.com/itripathiharsh" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.02c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A4.8 4.8 0 0 0 9 18.22v3.78"/><path d="M9 18.22c-3.23.95-3.23-2.03-5.23-2.03"/></svg> GitHub
          </a>
          <a href="mailto:harsh.tripathi.cs@gmail.com" className="hover:text-white transition-colors flex items-center gap-2">
            <Mail className="w-4 h-4" /> Contact
          </a>
        </div>
        <p className="tracking-widest uppercase text-xs font-semibold">MADE BY Harsh vvardhan tripathi</p>
        <p className="text-gray-600">&copy; {new Date().getFullYear()} Project DNA.</p>
      </div>
    </footer>
  );
};

// -----------------------------------------------------------------------------
// Main Landing Page Component
// -----------------------------------------------------------------------------
export default function Landing() {
  return (
    <SmoothScroll>
      <div className="min-h-screen bg-[#000] text-white font-sans selection:bg-white/20">
        
        {/* Minimal Nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex justify-between items-center bg-[#000]/50 backdrop-blur-xl border-b border-white/5">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo(0,0)}>
            <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-black font-black text-xl">
              D
            </div>
            <span className="font-bold text-white tracking-wide">Project DNA</span>
          </div>
          <a href="/onboarding" className="text-sm font-medium text-gray-400 hover:text-white transition-colors">
            Launch App &rarr;
          </a>
        </nav>

        <main>
          <Hero />
          <PipelineSection />
          <CodeCitySection />
          <TerminalSection />
        </main>
        
        <CTAFooter />
      </div>
    </SmoothScroll>
  );
}
