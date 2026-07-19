import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useMotionTemplate, useMotionValue } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Sphere, Line, Preload, Points, PointMaterial } from '@react-three/drei';
import Lenis from 'lenis';
import * as THREE from 'three';
import { Terminal, Network, BrainCircuit, ShieldAlert, Cpu, ChevronRight, Mail, GitPullRequest, Code2, Zap } from 'lucide-react';

// -----------------------------------------------------------------------------
// 1. Smooth Scrolling Wrapper
// -----------------------------------------------------------------------------
const SmoothScroll = ({ children }) => {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.5,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      smooth: true,
      smoothTouch: false,
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
// 2. High-End 3D Particles (Abstract DNA/Data stream)
// -----------------------------------------------------------------------------
const DataParticles = () => {
  const ref = useRef();
  
  const particlesCount = 3000;
  const positions = useMemo(() => {
    const pos = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount; i++) {
      const r = Math.random() * 10 + 2;
      const theta = 2 * Math.PI * Math.random();
      const z = (Math.random() - 0.5) * 40;
      pos[i * 3] = r * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(theta);
      pos[i * 3 + 2] = z;
    }
    return pos;
  }, [particlesCount]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (ref.current) {
      ref.current.rotation.z = t * 0.05;
      ref.current.rotation.y = Math.sin(t * 0.1) * 0.2;
    }
  });

  return (
    <group ref={ref}>
      <Points positions={positions} stride={3} frustumCulled={false}>
        <PointMaterial transparent color="#ffffff" size={0.03} sizeAttenuation={true} depthWrite={false} opacity={0.4} />
      </Points>
    </group>
  );
};

// -----------------------------------------------------------------------------
// 3. Floating Node Graph (Premium Abstract)
// -----------------------------------------------------------------------------
const AbstractGraph = () => {
  const groupRef = useRef();
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.15;
      groupRef.current.rotation.x = Math.sin(t * 0.1) * 0.1;
    }
  });

  const nodes = useMemo(() => {
    return Array.from({ length: 25 }, () => new THREE.Vector3(
      (Math.random() - 0.5) * 8,
      (Math.random() - 0.5) * 8,
      (Math.random() - 0.5) * 8
    ));
  }, []);

  const lines = useMemo(() => {
    const arr = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].distanceTo(nodes[j]) < 3.5) {
          arr.push([nodes[i], nodes[j]]);
        }
      }
    }
    return arr;
  }, [nodes]);

  return (
    <group ref={groupRef}>
      {nodes.map((pos, i) => (
        <Sphere key={i} args={[0.08, 16, 16]} position={pos}>
          <meshBasicMaterial color={i % 3 === 0 ? "#fff" : "#666"} transparent opacity={0.8} />
        </Sphere>
      ))}
      {lines.map((pts, i) => (
        <Line key={i} points={pts} color="#444" lineWidth={1} transparent opacity={0.2} />
      ))}
    </group>
  );
};

// -----------------------------------------------------------------------------
// 4. Glow Background & Grid Overlays
// -----------------------------------------------------------------------------
const BackgroundOverlay = () => (
  <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-black">
    {/* Subtle grid pattern */}
    <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    
    {/* Animated glow blobs */}
    <motion.div 
      animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
      transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-purple-900/30 rounded-full blur-[120px]" 
    />
    <motion.div 
      animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.4, 0.2] }}
      transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      className="absolute top-1/2 -left-40 w-[500px] h-[500px] bg-blue-900/20 rounded-full blur-[120px]" 
    />
  </div>
);

// -----------------------------------------------------------------------------
// 5. Hero Section (Ultra Premium)
// -----------------------------------------------------------------------------
const Hero = () => {
  const navigate = useNavigate();
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, 200]);
  const opacity = useTransform(scrollY, [0, 500], [1, 0]);

  return (
    <motion.section style={{ y, opacity }} className="relative min-h-screen w-full flex flex-col items-center justify-center pt-20 px-6 z-10">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 20], fov: 60 }}>
          <ambientLight intensity={0.1} />
          <DataParticles />
          <Preload all />
        </Canvas>
      </div>

      <div className="relative z-10 flex flex-col items-center text-center max-w-5xl mx-auto">
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-md mb-8"
        >
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span className="text-xs font-medium tracking-widest text-gray-300 uppercase">The Software Intelligence Engine</span>
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
          className="text-6xl md:text-8xl lg:text-9xl font-black text-white tracking-tighter leading-[0.9] mb-8"
        >
          Decode Your <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500">
            Architecture.
          </span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          className="text-xl md:text-2xl text-gray-400 max-w-2xl mb-12 font-light leading-relaxed"
        >
          Transform raw source code into a living, queryable knowledge graph. 
          Uncover hidden risks, technical debt, and architectural flaws instantly.
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center gap-6"
        >
          <button
            onClick={() => navigate('/onboarding')}
            className="group relative inline-flex items-center gap-2 px-8 py-4 bg-white text-black font-semibold rounded-full overflow-hidden transition-transform active:scale-95"
          >
            <div className="absolute inset-0 w-full h-full bg-gray-200 opacity-0 group-hover:opacity-100 transition-opacity" />
            <span className="relative z-10 flex items-center gap-2">
              Initialize Workspace
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </span>
          </button>
          
          <a href="#pipeline" className="text-gray-400 hover:text-white font-medium transition-colors flex items-center gap-2">
            Explore Engine <ChevronRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>
      
      {/* Scroll indicator */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3"
      >
        <span className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">Scroll</span>
        <div className="w-[1px] h-12 bg-gradient-to-b from-gray-500 to-transparent" />
      </motion.div>
    </motion.section>
  );
};

// -----------------------------------------------------------------------------
// 6. Premium Bento Grid (Features)
// -----------------------------------------------------------------------------
const BentoCard = ({ children, className = "", delay = 0 }) => {
  const [mouseX, setMouseX] = useState(0);
  const [mouseY, setMouseY] = useState(0);

  function handleMouseMove({ currentTarget, clientX, clientY }) {
    const { left, top } = currentTarget.getBoundingClientRect();
    setMouseX(clientX - left);
    setMouseY(clientY - top);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
      onMouseMove={handleMouseMove}
      className={`relative group rounded-3xl bg-[#050505] border border-white/10 overflow-hidden ${className}`}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-3xl opacity-0 group-hover:opacity-100 transition duration-500"
        style={{
          background: useMotionTemplate`radial-gradient(400px circle at ${mouseX}px ${mouseY}px, rgba(255,255,255,0.1), transparent 80%)`
        }}
      />
      {children}
    </motion.div>
  );
};

const PipelineSection = () => {
  return (
    <section id="pipeline" className="py-40 px-6 relative z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-24">
          <h2 className="text-4xl md:text-6xl font-black text-white tracking-tighter mb-6">
            The Intelligence Pipeline.
          </h2>
          <p className="text-gray-400 text-xl max-w-2xl mx-auto font-light leading-relaxed">
            A deterministic engine that reads code like a compiler, but reasons about it like an architect.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[320px]">
          
          <BentoCard className="md:col-span-2 md:row-span-2 p-10 flex flex-col justify-end" delay={0}>
            <div className="absolute inset-0 z-0 opacity-40 mix-blend-screen pointer-events-none">
              <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
                <AbstractGraph />
              </Canvas>
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-[#050505]/40 to-transparent z-10" />
            <div className="relative z-20">
              <Network className="w-12 h-12 text-white mb-6" />
              <h3 className="text-4xl font-bold text-white mb-4 tracking-tight">Entity Graph Mapping</h3>
              <p className="text-gray-400 text-lg max-w-md leading-relaxed font-light">
                Every function, class, and module is mapped into a rich multi-dimensional graph. Discover hidden dependencies and circular references instantly.
              </p>
            </div>
          </BentoCard>

          <BentoCard className="p-8 flex flex-col justify-between" delay={0.1}>
            <Code2 className="w-8 h-8 text-gray-300" />
            <div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">AST Parsing</h3>
              <p className="text-gray-400 text-sm leading-relaxed font-light">
                Lightning fast static analysis. We parse the syntax tree to extract deep structural evidence without executing your code.
              </p>
            </div>
          </BentoCard>

          <BentoCard className="p-8 flex flex-col justify-between bg-gradient-to-br from-[#050505] to-[#111]" delay={0.2}>
            <BrainCircuit className="w-8 h-8 text-white" />
            <div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">AI Reasoning</h3>
              <p className="text-gray-400 text-sm leading-relaxed font-light">
                No hallucinations. Our AI uses explicit codebase evidence to generate exact, actionable refactoring recommendations.
              </p>
            </div>
          </BentoCard>

        </div>
      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 7. Interactive Terminal / Real-time Output
// -----------------------------------------------------------------------------
const TerminalSection = () => {
  const [text, setText] = useState('');
  const fullText = `> Executing Project DNA Engine...
> Reading repository structure...
> Extracting AST from 1,204 files... [DONE 0.4s]
> Constructing entity graph... [DONE 0.2s]
> Detecting circular references... [FOUND 3]
> Analyzing security hotspots... [FOUND 1]
> Compiling churn & complexity metrics... [DONE]
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
    <section className="py-40 px-6 relative z-10 border-t border-white/5">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        
        <div className="order-2 lg:order-1 relative group w-full">
          <div className="absolute -inset-1 bg-gradient-to-r from-gray-800 to-gray-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000" />
          <div className="relative rounded-2xl border border-white/10 bg-[#0a0a0a] overflow-hidden shadow-2xl">
            <div className="flex items-center px-4 py-3 bg-[#111] border-b border-white/5 gap-2">
              <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
              <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
              <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
              <div className="ml-4 text-[10px] text-gray-500 font-mono tracking-widest uppercase">engine ~ process</div>
            </div>
            <div className="p-6 font-mono text-sm text-gray-300 min-h-[300px] leading-relaxed whitespace-pre-wrap">
              {text}
              <span className="animate-pulse inline-block w-2 h-4 bg-gray-300 ml-1 translate-y-1" />
            </div>
          </div>
        </div>

        <div className="order-1 lg:order-2 space-y-8">
          <h2 className="text-4xl md:text-5xl font-black text-white leading-tight tracking-tighter">
            Real-time <br />
            Intelligence.
          </h2>
          <p className="text-lg text-gray-400 font-light leading-relaxed">
            Ask complex architectural questions in plain English. The engine traces the exact files, dependencies, and historical commits to give you a definitive answer.
          </p>
          
          <ul className="space-y-6 pt-4">
            {[
              { icon: Zap, text: 'Predictive Analytics & Forecasting' },
              { icon: GitPullRequest, text: 'Automated Refactoring Suite' },
              { icon: ShieldAlert, text: 'Security & Risk Heatmaps' },
            ].map((item, i) => (
              <motion.li 
                key={i} 
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="flex items-center gap-4 text-gray-300 font-medium"
              >
                <div className="w-10 h-10 rounded-full bg-[#111] border border-white/10 flex items-center justify-center">
                  <item.icon className="w-4 h-4 text-white" />
                </div>
                {item.text}
              </motion.li>
            ))}
          </ul>
        </div>

      </div>
    </section>
  );
};

// -----------------------------------------------------------------------------
// 8. Footer / Final CTA
// -----------------------------------------------------------------------------
const Footer = () => {
  const navigate = useNavigate();
  return (
    <footer className="relative flex flex-col items-center justify-center overflow-hidden border-t border-white/10 pt-40 pb-12 px-6 z-10 bg-[#000]">
      
      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-20 text-center max-w-3xl mb-40"
      >
        <h2 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tighter">Stop Guessing.</h2>
        <p className="text-xl text-gray-400 mb-12 font-light leading-relaxed">
          The future of software intelligence is here. Start analyzing your repositories with deterministic precision today.
        </p>
        
        <button
          onClick={() => navigate('/onboarding')}
          className="px-10 py-5 bg-white text-black font-semibold rounded-full hover:scale-105 transition-transform duration-300"
        >
          Initialize Workspace
        </button>
      </motion.div>

      {/* Credits */}
      <div className="relative z-20 w-full max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-gray-500 text-sm border-t border-white/5 pt-8">
        <div className="flex items-center gap-2 font-medium tracking-wide">
          <div className="w-6 h-6 rounded bg-white flex items-center justify-center text-black font-black text-xs mr-2">D</div>
          Project DNA
        </div>
        
        <div className="flex items-center gap-6">
          <a href="https://github.com/itripathiharsh" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.02c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A4.8 4.8 0 0 0 9 18.22v3.78"/><path d="M9 18.22c-3.23.95-3.23-2.03-5.23-2.03"/></svg>
            GitHub
          </a>
          <a href="mailto:harsh.tripathi.cs@gmail.com" className="hover:text-white transition-colors flex items-center gap-2">
            <Mail className="w-4 h-4" /> Contact
          </a>
        </div>

        <div className="text-right">
          <p className="tracking-widest uppercase text-[10px] font-bold text-gray-400 mb-1">Made By</p>
          <p className="text-gray-300 font-medium tracking-wide">Harsh Vardhan Tripathi</p>
        </div>
      </div>
    </footer>
  );
};

// -----------------------------------------------------------------------------
// Main Component
// -----------------------------------------------------------------------------
export default function Landing() {
  return (
    <SmoothScroll>
      <div className="min-h-screen bg-[#000] text-white font-sans selection:bg-white/20">
        <BackgroundOverlay />
        
        {/* Minimal Nav */}
        <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-6 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
          <div className="flex items-center gap-3 pointer-events-auto cursor-pointer" onClick={() => window.scrollTo(0,0)}>
            <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-black font-black text-xl">D</div>
            <span className="font-bold text-white tracking-wide">Project DNA</span>
          </div>
          <button 
            onClick={() => window.location.href='/onboarding'} 
            className="pointer-events-auto text-sm font-medium text-gray-400 hover:text-white transition-colors px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md"
          >
            Launch App
          </button>
        </nav>

        <main>
          <Hero />
          <PipelineSection />
          <TerminalSection />
        </main>
        
        <Footer />
      </div>
    </SmoothScroll>
  );
}
