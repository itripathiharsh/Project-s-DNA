import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, AnimatePresence, useSpring } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Float, Box, Sphere, MeshDistortMaterial } from '@react-three/drei';
import Lenis from 'lenis';
import * as THREE from 'three';

// -----------------------------------------------------------------------------
// 1. Smooth Scrolling Wrapper (Lenis)
// -----------------------------------------------------------------------------
const SmoothScroll = ({ children }) => {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      gestureDirection: 'vertical',
      smooth: true,
      mouseMultiplier: 1,
      smoothTouch: false,
      touchMultiplier: 2,
      infinite: false,
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
      groupRef.current.rotation.y = t * 0.2;
    }
  });

  const numPairs = 20;
  const radius = 2;
  const height = 10;
  const pairs = useMemo(() => {
    const arr = [];
    for (let i = 0; i < numPairs; i++) {
      const y = (i / numPairs - 0.5) * height;
      const angle = i * 0.4;
      arr.push({ id: i, y, angle });
    }
    return arr;
  }, [numPairs]);

  return (
    <group ref={groupRef} position={[0, 0, 0]}>
      {pairs.map((p) => (
        <group key={p.id} position={[0, p.y, 0]} rotation={[0, p.angle, 0]}>
          <Sphere args={[0.3, 16, 16]} position={[-radius, 0, 0]}>
            <MeshDistortMaterial color="#9d4edd" emissive="#5a189a" emissiveIntensity={0.5} distort={0.2} />
          </Sphere>
          <Sphere args={[0.3, 16, 16]} position={[radius, 0, 0]}>
            <MeshDistortMaterial color="#00f5d4" emissive="#00bbf9" emissiveIntensity={0.5} distort={0.2} />
          </Sphere>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.05, 0.05, radius * 2]} />
            <meshStandardMaterial color="#4a4e69" transparent opacity={0.6} />
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
      cityRef.current.rotation.y = Math.sin(t * 0.1) * 0.1;
    }
  });

  const buildings = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 50; i++) {
      const x = (Math.random() - 0.5) * 20;
      const z = (Math.random() - 0.5) * 20;
      const h = Math.random() * 5 + 1;
      const color = Math.random() > 0.8 ? '#f15bb5' : Math.random() > 0.5 ? '#9b5de5' : '#00bbf9';
      arr.push({ x, z, h, color });
    }
    return arr;
  }, []);

  return (
    <group ref={cityRef}>
      {buildings.map((b, i) => (
        <Box key={i} args={[0.8, b.h, 0.8]} position={[b.x, b.h / 2 - 2, b.z]}>
          <meshStandardMaterial color={b.color} emissive={b.color} emissiveIntensity={0.2} wireframe={Math.random() > 0.8} />
        </Box>
      ))}
      <gridHelper args={[30, 30, '#4a4e69', '#22223b']} position={[0, -2, 0]} />
    </group>
  );
};

// -----------------------------------------------------------------------------
// 4. Hero Section
// -----------------------------------------------------------------------------
const Hero = () => {
  const navigate = useNavigate();
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, 300]);
  const opacity = useTransform(scrollY, [0, 500], [1, 0]);

  return (
    <motion.section 
      style={{ y, opacity }}
      className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden"
    >
      <div className="absolute inset-0 z-0 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 15], fov: 40 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
            <DNAHelix />
          </Float>
        </Canvas>
      </div>

      <div className="z-10 text-center px-4 max-w-4xl flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="px-4 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-semibold mb-6 backdrop-blur-md"
        >
          Project DNA Platform
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.1 }}
          className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-gray-200 to-gray-500 tracking-tight leading-tight mb-6"
        >
          Understand Software. <br className="hidden md:block"/> Completely.
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
          className="text-lg md:text-xl text-text-muted max-w-2xl mb-10 leading-relaxed"
        >
          Transform any repository into a living, interactive knowledge graph. 
          Discover architectural flaws, mitigate risks, and let the AI guide your next refactor.
        </motion.p>
        
        <motion.button
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
          onClick={() => navigate('/onboarding')}
          className="group relative px-8 py-4 bg-primary text-white font-bold rounded-full overflow-hidden shadow-[0_0_40px_rgba(157,78,221,0.4)] hover:shadow-[0_0_60px_rgba(157,78,221,0.6)] transition-all duration-300"
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-in-out" />
          <span className="relative z-10 flex items-center gap-2">
            Analyze Repository
            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </span>
        </motion.button>
      </div>

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-text-muted animate-bounce">
        <span className="text-xs tracking-widest uppercase">Scroll to explore</span>
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </motion.section>
  );
};

// -----------------------------------------------------------------------------
// 5. Pipeline / Flow Section
// -----------------------------------------------------------------------------
const PipelineSection = () => {
  const steps = [
    { title: "Repository", desc: "Connect any Git repo.", icon: "📂" },
    { title: "AST Parsing", desc: "Deep structural analysis.", icon: "🌳" },
    { title: "Knowledge Graph", desc: "Map all dependencies.", icon: "🕸️" },
    { title: "AI Intelligence", desc: "Insights & recommendations.", icon: "🧠" }
  ];

  return (
    <section className="py-32 px-6 relative z-10 bg-surface">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">The DNA Pipeline</h2>
          <p className="text-text-muted text-lg max-w-2xl mx-auto">From raw source code to a fully queryable, AI-driven knowledge base in seconds.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {steps.map((step, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: i * 0.15 }}
              className="p-6 rounded-2xl bg-surface-container/50 border border-border-subtle backdrop-blur-md hover:bg-surface-container/80 transition-colors group relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-4xl mb-4 relative z-10">{step.icon}</div>
              <h3 className="text-xl font-bold text-white mb-2 relative z-10">{step.title}</h3>
              <p className="text-text-muted text-sm relative z-10">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 6. Interactive Code City Section
// -----------------------------------------------------------------------------
const CodeCitySection = () => {
  return (
    <section className="h-[80vh] w-full relative bg-[#050508] border-y border-border-subtle overflow-hidden">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [15, 10, 15], fov: 45 }}>
          <ambientLight intensity={0.3} />
          <directionalLight position={[10, 20, 10]} intensity={1.5} color="#fff" />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
          <CodeCity />
        </Canvas>
      </div>
      
      <div className="absolute inset-0 z-10 pointer-events-none bg-gradient-to-b from-[#050508] via-transparent to-[#050508]" />
      
      <div className="absolute top-1/2 left-10 -translate-y-1/2 z-20 max-w-md pointer-events-none">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="p-8 rounded-3xl bg-black/40 border border-white/10 backdrop-blur-xl shadow-2xl"
        >
          <h2 className="text-3xl font-bold text-white mb-4">Code City Visualization</h2>
          <p className="text-text-muted leading-relaxed">
            See your codebase differently. Folders become districts, files become buildings. 
            Height represents complexity, while glowing structures highlight critical paths and security hotspots.
          </p>
        </motion.div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 7. Live Terminal / Features Section
// -----------------------------------------------------------------------------
const TerminalSection = () => {
  const [text, setText] = useState('');
  const fullText = `> Connecting to Project DNA Engine...
> Extracting AST from 1,204 files... [DONE]
> Mapping dependencies... [DONE]
> Detecting circular references... [FOUND 3]
> Analyzing security hotspots...
> Generating architectural summary...
> 
> SYSTEM READY. Awaiting intelligence queries.`;

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setText(fullText.substring(0, i));
      i++;
      if (i > fullText.length) clearInterval(interval);
    }, 20);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-32 px-6 bg-surface relative overflow-hidden">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-16 items-center">
        
        <div className="flex-1 space-y-8">
          <h2 className="text-4xl md:text-5xl font-bold text-white leading-tight">
            Real-time <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-cyan to-signal-blue">Intelligence</span>
          </h2>
          <p className="text-lg text-text-muted">
            The reasoning engine doesn't just parse text; it builds a deterministic semantic graph of your entire architecture. 
            Ask complex questions, simulate refactoring impacts, and generate production-ready documentation instantly.
          </p>
          
          <ul className="space-y-4">
            {['Predictive Analytics & Forecasting', 'Automated Refactoring Suite', 'Security & Risk Heatmaps', 'Semantic Repository Search'].map((feature, i) => (
              <li key={i} className="flex items-center gap-3 text-white">
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-primary border border-primary/30">✓</div>
                {feature}
              </li>
            ))}
          </ul>
        </div>

        <div className="flex-1 w-full">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="rounded-xl overflow-hidden border border-border-subtle shadow-2xl bg-[#0a0a0f]"
          >
            <div className="flex items-center px-4 py-3 bg-[#111116] border-b border-border-subtle gap-2">
              <div className="w-3 h-3 rounded-full bg-signal-rose" />
              <div className="w-3 h-3 rounded-full bg-signal-amber" />
              <div className="w-3 h-3 rounded-full bg-signal-green" />
              <div className="ml-4 text-xs text-text-muted font-mono">dna-engine ~ bash</div>
            </div>
            <div className="p-6 font-mono text-sm text-signal-cyan h-64 overflow-y-auto whitespace-pre-wrap">
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
// 8. Final CTA Section
// -----------------------------------------------------------------------------
const CTASection = () => {
  const navigate = useNavigate();
  return (
    <section className="py-40 px-6 relative flex flex-col items-center justify-center overflow-hidden border-t border-border-subtle">
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 10] }}>
          <ambientLight intensity={0.5} />
          <Stars radius={50} depth={20} count={2000} factor={4} saturation={0} fade />
          <Float speed={2} floatIntensity={2}>
            <DNAHelix />
          </Float>
        </Canvas>
      </div>
      
      <div className="absolute inset-0 bg-surface/80 backdrop-blur-sm z-10" />

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-20 text-center max-w-2xl"
      >
        <h2 className="text-5xl md:text-7xl font-black text-white mb-6">Ready to Decode?</h2>
        <p className="text-xl text-text-muted mb-10">Stop guessing. Start understanding. The future of software intelligence is here.</p>
        
        <button
          onClick={() => navigate('/onboarding')}
          className="px-10 py-5 bg-white text-black font-bold text-lg rounded-full overflow-hidden hover:scale-105 transition-transform duration-300 shadow-[0_0_50px_rgba(255,255,255,0.3)]"
        >
          Initialize Workspace
        </button>
      </motion.div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// Main Landing Page Component
// -----------------------------------------------------------------------------
export default function Landing() {
  return (
    <SmoothScroll>
      <div className="min-h-screen bg-surface text-on-surface font-sans selection:bg-primary/30">
        
        {/* Minimal Nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex justify-between items-center bg-surface/50 backdrop-blur-xl border-b border-white/5">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo(0,0)}>
            <div className="w-8 h-8 rounded bg-gradient-to-br from-primary to-signal-blue flex items-center justify-center text-white font-black text-xl shadow-[0_0_15px_rgba(157,78,221,0.5)]">
              D
            </div>
            <span className="font-bold text-white tracking-wide">Project DNA</span>
          </div>
          <a href="/onboarding" className="text-sm font-medium text-text-muted hover:text-white transition-colors">Launch App &rarr;</a>
        </nav>

        <main>
          <Hero />
          <PipelineSection />
          <CodeCitySection />
          <TerminalSection />
          <CTASection />
        </main>
        
        <footer className="py-8 text-center text-text-muted text-sm border-t border-border-subtle bg-surface relative z-20">
          &copy; {new Date().getFullYear()} Project DNA. Understand Software. Completely.
        </footer>
      </div>
    </SmoothScroll>
  );
}
