import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'

/* ═══════════════════════════════════════════════════════════════════
   SICP LANDING PAGE — Government Digital Portal
   Inspired by u.ae/en with Liquid Glass + Glassmorphism
   ═══════════════════════════════════════════════════════════════════ */

// ─── Hero Carousel Slides ────────────────────────────────────────
const HERO_SLIDES = [
  {
    image: '/carousels1.jpeg',
    title: 'Solving Real Problems.\nBuilding a Better Jharkhand Together.',
    subtitle: 'SICP connects citizens, universities and industry to collaborate on real-world challenges across Jharkhand.',
    overlay: 'linear-gradient(135deg, rgba(14,72,42,0.85) 0%, rgba(23,108,59,0.7) 50%, rgba(14,72,42,0.5) 100%)',
  },
  {
    image: '/carousels2.jpeg',
    title: 'Crowdsource Solutions.\nEmpower Communities.',
    subtitle: 'Submit real problems, get innovative solutions from universities and industry partners working together.',
    overlay: 'linear-gradient(135deg, rgba(9,51,30,0.85) 0%, rgba(23,108,59,0.7) 50%, rgba(39,132,77,0.5) 100%)',
  },
  {
    image: '/carousels3.jpeg',
    title: 'University & Industry\nCollaboration Network.',
    subtitle: '18 universities and 96 industry partners driving innovation across every district of Jharkhand.',
    overlay: 'linear-gradient(135deg, rgba(14,72,42,0.85) 0%, rgba(26,128,72,0.7) 50%, rgba(39,132,77,0.5) 100%)',
  },
  {
    image: '/carousels4.jpeg',
    title: 'Track Impact.\nMeasure Change.',
    subtitle: 'Real-time analytics showing 2.4M+ people impacted and 12,458 problems addressed through collaborative action.',
    overlay: 'linear-gradient(135deg, rgba(9,51,30,0.85) 0%, rgba(23,108,59,0.7) 50%, rgba(14,72,42,0.5) 100%)',
  },
  {
    image: '/carousels5.jpeg',
    title: 'Transparent Governance.\nReal Results.',
    subtitle: 'Experience seamless collaboration between citizens and administration.',
    overlay: 'linear-gradient(135deg, rgba(14,72,42,0.85) 0%, rgba(23,108,59,0.7) 50%, rgba(14,72,42,0.5) 100%)',
  },
]

// ─── SVG ICONS ───────────────────────────────────────────────────
const Icons = {
  Clipboard: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" /></svg>,
  Lightning: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z" /></svg>,
  Graduation: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347m-15.482 0a50.636 50.636 0 0 0-2.658-.813A59.906 59.906 0 0 1 12 3.493a59.903 59.903 0 0 1 10.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.717 50.717 0 0 1 12 13.489a50.702 50.702 0 0 1 7.74-3.342M6.75 15a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm0 0v-3.675A55.378 55.378 0 0 1 12 8.443m-7.007 11.55A5.981 5.981 0 0 0 6.75 15.75v-1.5" /></svg>,
  Factory: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0 0 12 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75Z" /></svg>,
  Users: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" /></svg>,
  Document: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" /></svg>,
  CheckCircle: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>,
  AI: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Zm.75-12h9v9h-9v-9Z" /></svg>,
  Target: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15.042 21.672 13.684 16.6m0 0-2.51 2.225.569-9.47 5.227 7.917-3.286-.672ZM12 2.25V4.5m5.834.166-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243-1.59-1.59" /></svg>,
  Rocket: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.499 4.499 0 0 0-1.757 4.306 4.499 4.499 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z" /></svg>,
  WaterDrop: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S12 3 12 3s-4.5 4.97-4.5 9 2.015 9 4.5 9Z" /></svg>,
  Building: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Zm0 3h.008v.008h-.008v-.008Z" /></svg>,
  Leaf: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9 3.75H6.912a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H15M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859M12 3v8.25m0 0-3-3m3 3 3-3" /></svg>,
  Medical: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" /></svg>,
  Book: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" /></svg>,
  Globe: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S12 3 12 3s-4.5 4.97-4.5 9 2.015 9 4.5 9Z" /></svg>,
  Gear: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>,
  Chart: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" /></svg>,
  Computer: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 0 1-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0 1 15 18.257V17.25m6-12V15a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25" /></svg>,
  Hammer: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.492-3.396c.339-.462.1-1.094-.433-1.277-.895-.307-1.927-.391-2.936-.184a4.5 4.5 0 0 0-3.66 3.66c-.206 1.01-.122 2.041.184 2.936.183.532.814.772 1.277.433l3.396-2.492Z" /><path strokeLinecap="round" strokeLinejoin="round" d="m15.17 11.42-3.396 2.492c-.462.339-1.094.1-1.277-.433a7.13 7.13 0 0 1-.184-2.936 4.5 4.5 0 0 1 3.66-3.66c1.01-.206 2.041-.122 2.936.184.532.183.772.814.433 1.277l-2.492 3.396Z" /></svg>,
  Pickaxe: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M3 21l8-8m5-5 5-5m0 0v5m0-5h-5" /></svg>,
  Wrench: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.492-3.396c.339-.462.1-1.094-.433-1.277-.895-.307-1.927-.391-2.936-.184a4.5 4.5 0 0 0-3.66 3.66c-.206 1.01-.122 2.041.184 2.936.183.532.814.772 1.277.433l3.396-2.492Z" /></svg>,
  Link: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" /></svg>,
  Search: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>,
  Megaphone: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 1 1 0-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 0 1-1.44-4.282m3.102.069a18.03 18.03 0 0 1-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 0 1 8.835 2.535M10.34 6.66a23.847 23.847 0 0 0 8.835-2.535m0 0A23.74 23.74 0 0 0 18.795 3m.38 1.125a23.91 23.91 0 0 1 1.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 0 0 1.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 0 1 0 3.46" /></svg>,
  Process: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12a7.5 7.5 0 0 0 15 0m-15 0a7.5 7.5 0 1 1 15 0m-15 0H3m16.5 0H21m-1.5 0a7.5 7.5 0 1 1-15 0m15 0a7.5 7.5 0 1 0-15 0" /></svg>,
  Sparkles: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09l2.846.813-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" /></svg>,
  Handshake: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" /></svg>,
  Sprout: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0 0 12 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75Z" /></svg>,
  MapPin: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" /></svg>,
  Phone: <svg className="w-full h-full currentColor" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 0 0 6 3.75v16.5a2.25 2.25 0 0 0 2.25 2.25h7.5A2.25 2.25 0 0 0 18 20.25V3.75a2.25 2.25 0 0 0-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3" /></svg>,
}

// ─── Stats Data ──────────────────────────────────────────────────
const STATS = [
  { icon: <div className="w-6 h-6">{Icons.Clipboard}</div>, label: 'Problems Reported', value: '12,458', color: 'green' },
  { icon: <div className="w-6 h-6">{Icons.Lightning}</div>, label: 'Active Projects', value: '1,243', color: 'blue' },
  { icon: <div className="w-6 h-6">{Icons.Graduation}</div>, label: 'Universities', value: '18', color: 'gold' },
  { icon: <div className="w-6 h-6">{Icons.Factory}</div>, label: 'Industry Partners', value: '96', color: 'rose' },
  { icon: <div className="w-6 h-6">{Icons.Users}</div>, label: 'People Impacted', value: '2.4M+', color: 'violet' },
]

// ─── How It Works Steps ──────────────────────────────────────────
const STEPS = [
  { num: '01', title: 'Submit', desc: 'Citizen submits a real-world problem with evidence and location', icon: <div className="w-8 h-8 text-emerald-600 mx-auto mb-2">{Icons.Document}</div> },
  { num: '02', title: 'Validate', desc: 'Community upvotes and moderator verifies the report', icon: <div className="w-8 h-8 text-emerald-600 mx-auto mb-2">{Icons.CheckCircle}</div> },
  { num: '03', title: 'AI Process', desc: 'AI classifies, prioritises and clusters similar problems', icon: <div className="w-8 h-8 text-emerald-600 mx-auto mb-2">{Icons.AI}</div> },
  { num: '04', title: 'Route', desc: 'Routed to the best matching university team for solution', icon: <div className="w-8 h-8 text-emerald-600 mx-auto mb-2">{Icons.Target}</div> },
  { num: '05', title: 'Impact', desc: 'Solution deployed, impact measured and reported back', icon: <div className="w-8 h-8 text-emerald-600 mx-auto mb-2">{Icons.Rocket}</div> },
]

// ─── Featured Problems ──────────────────────────────────────────
const PROBLEMS = [
  { tag: 'Water & Sanitation', tagClass: 'water', priority: 'High Priority', title: 'Drinking Water Contamination in Hulhundu Village', location: 'Gumla, Jharkhand', upvotes: 132, team: 'NIT Jamshedpur', status: 'In Progress' },
  { tag: 'Infrastructure', tagClass: 'infra', priority: 'Medium', title: 'Road Connectivity Issues in Remote Tribal Areas', location: 'Khunti, Jharkhand', upvotes: 89, team: 'BIT Mesra', status: 'Routed' },
  { tag: 'Healthcare', tagClass: 'health', priority: 'High Priority', title: 'Lack of Primary Healthcare Center in Rural Block', location: 'Latehar, Jharkhand', upvotes: 215, team: 'RIMS Ranchi', status: 'Proposed' },
  { tag: 'Environment', tagClass: 'env', priority: 'Medium', title: 'Deforestation & Soil Erosion Near Subarnarekha River', location: 'Seraikela, Jharkhand', upvotes: 167, team: 'IIT(ISM) Dhanbad', status: 'In Progress' },
  { tag: 'Education', tagClass: 'edu', priority: 'Low', title: 'Digital Literacy Gap in Government Schools', location: 'Palamu, Jharkhand', upvotes: 98, team: 'Ranchi University', status: 'Validated' },
  { tag: 'Water & Sanitation', tagClass: 'water', priority: 'High Priority', title: 'Arsenic Contamination in Tube Wells', location: 'Sahebganj, Jharkhand', upvotes: 203, team: 'NIT Jamshedpur', status: 'Pilot Testing' },
]

// ─── Category Data ───────────────────────────────────────────────
const CATEGORIES = [
  { icon: <div className="w-10 h-10 mx-auto text-cyan-500 mb-3">{Icons.WaterDrop}</div>, name: 'Water & Sanitation', count: '3,987', color: 'from-cyan-400/20 to-cyan-500/5' },
  { icon: <div className="w-10 h-10 mx-auto text-amber-500 mb-3">{Icons.Building}</div>, name: 'Infrastructure', count: '2,990', color: 'from-amber-400/20 to-amber-500/5' },
  { icon: <div className="w-10 h-10 mx-auto text-emerald-500 mb-3">{Icons.Leaf}</div>, name: 'Environment', count: '2,242', color: 'from-emerald-400/20 to-emerald-500/5' },
  { icon: <div className="w-10 h-10 mx-auto text-rose-500 mb-3">{Icons.Medical}</div>, name: 'Healthcare', count: '1,869', color: 'from-rose-400/20 to-rose-500/5' },
  { icon: <div className="w-10 h-10 mx-auto text-violet-500 mb-3">{Icons.Book}</div>, name: 'Education', count: '997', color: 'from-violet-400/20 to-violet-500/5' },
  { icon: <div className="w-10 h-10 mx-auto text-yellow-500 mb-3">{Icons.Lightning}</div>, name: 'Energy', count: '623', color: 'from-yellow-400/20 to-yellow-500/5' },
]

// ─── Partners ────────────────────────────────────────────────────
const UNIVERSITY_PARTNERS = [
  { name: 'NIT\nJamshedpur', icon: <div className="w-8 h-8 mx-auto text-indigo-500">{Icons.Building}</div> },
  { name: 'IIT(ISM)\nDhanbad', icon: <div className="w-8 h-8 mx-auto text-blue-500">{Icons.Gear}</div> },
  { name: 'XLRI\nJamshedpur', icon: <div className="w-8 h-8 mx-auto text-green-500">{Icons.Chart}</div> },
  { name: 'BIT\nMesra', icon: <div className="w-8 h-8 mx-auto text-teal-500">{Icons.Computer}</div> },
  { name: 'Ranchi\nUniversity', icon: <div className="w-8 h-8 mx-auto text-yellow-600">{Icons.Graduation}</div> },
  { name: 'RIMS\nRanchi', icon: <div className="w-8 h-8 mx-auto text-red-500">{Icons.Medical}</div> },
]

const INDUSTRY_PARTNERS = [
  { name: 'Tata Steel\nFoundation', icon: <div className="w-8 h-8 mx-auto text-slate-700">{Icons.Factory}</div> },
  { name: 'SAIL\nBokaro', icon: <div className="w-8 h-8 mx-auto text-slate-600">{Icons.Hammer}</div> },
  { name: 'Coal India\nLimited', icon: <div className="w-8 h-8 mx-auto text-zinc-700">{Icons.Pickaxe}</div> },
  { name: 'HEC\nRanchi', icon: <div className="w-8 h-8 mx-auto text-slate-500">{Icons.Wrench}</div> },
  { name: 'Usha Martin\nLtd', icon: <div className="w-8 h-8 mx-auto text-stone-600">{Icons.Link}</div> },
]

/* ═══════════════════════════════════════════════════════════════════
   SCROLL REVEAL HOOK
   ═══════════════════════════════════════════════════════════════════ */
function useReveal() {
  const ref = useRef(null)
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible')
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    )
    const elements = ref.current?.querySelectorAll('.reveal')
    elements?.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])
  return ref
}

/* ═══════════════════════════════════════════════════════════════════
   ANIMATED COUNTER
   ═══════════════════════════════════════════════════════════════════ */
function AnimatedValue({ value }) {
  const [display, setDisplay] = useState('0')
  const ref = useRef(null)
  const animated = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !animated.current) {
          animated.current = true
          const numericPart = value.replace(/[^0-9.]/g, '')
          const suffix = value.replace(/[0-9.,]/g, '')
          const target = parseFloat(numericPart.replace(/,/g, ''))
          const hasDecimal = numericPart.includes('.')
          const duration = 1800
          const startTime = performance.now()

          const tick = (now) => {
            const elapsed = now - startTime
            const progress = Math.min(elapsed / duration, 1)
            const eased = 1 - Math.pow(1 - progress, 3)
            const current = target * eased

            if (hasDecimal) {
              setDisplay(current.toFixed(1).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix)
            } else {
              setDisplay(Math.floor(current).toLocaleString() + suffix)
            }

            if (progress < 1) requestAnimationFrame(tick)
          }
          requestAnimationFrame(tick)
        }
      },
      { threshold: 0.5 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [value])

  return <span ref={ref}>{display}</span>
}

/* ═══════════════════════════════════════════════════════════════════
   HERO SECTION WITH FULL-SCREEN CAROUSEL
   ═══════════════════════════════════════════════════════════════════ */
function HeroSection() {
  const [current, setCurrent] = useState(0)
  const timerRef = useRef(null)

  const goTo = useCallback((idx) => {
    setCurrent(idx)
    clearInterval(timerRef.current)
    timerRef.current = setInterval(() => setCurrent((p) => (p + 1) % HERO_SLIDES.length), 6000)
  }, [])

  useEffect(() => {
    timerRef.current = setInterval(() => setCurrent((p) => (p + 1) % HERO_SLIDES.length), 6000)
    return () => clearInterval(timerRef.current)
  }, [])

  const slide = HERO_SLIDES[current]

  return (
    <section id="hero" className="hero-section relative" style={{ minHeight: '100vh' }}>
      {/* Background Images */}
      {HERO_SLIDES.map((s, i) => (
        <div
          key={i}
          className="absolute inset-0 transition-opacity duration-1000 ease-in-out"
          style={{
            opacity: i === current ? 1 : 0,
            backgroundImage: `url(${s.image})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
      ))}

      {/* Gradient Overlay */}
      <div
        className="absolute inset-0 transition-all duration-1000"
        style={{ background: slide.overlay }}
      />

      {/* Animated Glass Orbs */}
      <div className="orb orb-green w-[500px] h-[500px] -right-40 -bottom-40 animate-float-slow" style={{ opacity: 0.2 }} />
      <div className="orb orb-gold w-[350px] h-[350px] left-[15%] -top-32 animate-float-slower" style={{ opacity: 0.15 }} />
      <div className="orb orb-blue w-[250px] h-[250px] right-[25%] top-[20%] animate-float" style={{ opacity: 0.1 }} />

      {/* Content */}
      <div className="relative z-10 max-w-[1400px] mx-auto px-4 sm:px-6 pt-32 pb-28 min-h-[100vh] flex flex-col justify-center">
        <div className="max-w-3xl">
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-white/90 text-xs font-bold tracking-widest uppercase mb-8 animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-soft" />
            Government of Jharkhand
          </div>

          {/* Title */}
          <h1
            className="font-display text-white leading-[1.05] tracking-tight animate-fade-in-up"
            style={{ fontSize: 'clamp(2.5rem, 5vw, 4.2rem)', fontWeight: 800, whiteSpace: 'pre-line' }}
          >
            {slide.title}
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-white/75 text-lg max-w-xl leading-relaxed animate-fade-in" style={{ animationDelay: '0.2s' }}>
            {slide.subtitle}
          </p>

          {/* Buttons */}
          <div className="flex flex-wrap gap-4 mt-10" style={{ animationDelay: '0.4s' }}>
            <Link to="/citizen" className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white text-primary-800 font-bold text-sm shadow-xl hover:shadow-2xl hover:-translate-y-0.5 transition-all duration-300">
              Report a Problem
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </Link>
            <button onClick={() => document.querySelector('#explore')?.scrollIntoView({ behavior: 'smooth' })} className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white font-bold text-sm hover:bg-white/20 transition-all duration-300">
              Explore Problems
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </button>
          </div>
        </div>

        {/* Carousel Dots */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex gap-2 z-20">
          {HERO_SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i)}
              className={`h-2 rounded-full transition-all duration-500 ${
                i === current ? 'w-10 bg-white' : 'w-2 bg-white/40 hover:bg-white/60'
              }`}
              aria-label={`Slide ${i + 1}`}
            />
          ))}
        </div>

        {/* Slide Counter */}
        <div className="absolute bottom-10 right-8 text-white/40 text-sm font-mono z-20">
          <span className="text-white font-bold text-lg">{String(current + 1).padStart(2, '0')}</span>
          <span className="mx-1">/</span>
          <span>{String(HERO_SLIDES.length).padStart(2, '0')}</span>
        </div>
      </div>

      {/* Bottom Glass Stats Strip */}
      <div className="absolute bottom-0 left-0 right-0 z-20">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6">
          <div className="hidden md:grid grid-cols-5 gap-0 rounded-t-2xl overflow-hidden liquid-glass" style={{
            background: 'rgba(255,255,255,0.12)',
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            borderTop: '1px solid rgba(255,255,255,0.15)',
            borderLeft: '1px solid rgba(255,255,255,0.1)',
            borderRight: '1px solid rgba(255,255,255,0.1)',
          }}>
            {STATS.map((s, i) => (
              <div key={s.label} className="flex items-center gap-3 px-5 py-4 border-r border-white/10 last:border-r-0">
                <span className="flex items-center justify-center">{s.icon}</span>
                <div>
                  <div className="text-[10px] text-white/50 font-medium uppercase tracking-wider">{s.label}</div>
                  <div className="text-white font-extrabold text-lg leading-tight mt-0.5"><AnimatedValue value={s.value} /></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   STATS SECTION (below hero on mobile)
   ═══════════════════════════════════════════════════════════════════ */
function StatsSection() {
  return (
    <div className="md:hidden stats-strip -mt-6 mb-8 px-4">
      <div className="stats-inner liquid-glass" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
        {STATS.map((s) => (
          <div key={s.label} className="stat-item" style={{ borderRight: 'none', borderBottom: '1px solid rgba(23,108,59,0.06)', paddingBottom: '0.75rem', marginBottom: '0.5rem' }}>
            <div className={`stat-icon ${s.color}`}>{s.icon}</div>
            <div>
              <div className="stat-label">{s.label}</div>
              <div className="stat-value" style={{ fontSize: '1.25rem' }}><AnimatedValue value={s.value} /></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   CATEGORY CARDS SECTION
   ═══════════════════════════════════════════════════════════════════ */
function CategoriesSection() {
  return (
    <section className="section-container" id="explore">
      <div className="text-center">
        <span className="section-eyebrow reveal flex items-center justify-center gap-1.5"><div className="w-4 h-4">{Icons.Search}</div> Explore Problems</span>
        <h2 className="section-title mx-auto reveal reveal-delay-1">Discover Challenges Across Jharkhand</h2>
        <p className="section-subtitle mx-auto text-center reveal reveal-delay-2">Browse problems by category and find opportunities to make a real difference in communities.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mt-12">
        {CATEGORIES.map((cat, i) => (
          <div
            key={cat.name}
            className={`reveal reveal-delay-${Math.min(i + 1, 5)} group cursor-pointer rounded-2xl p-6 text-center transition-all duration-300 bg-gradient-to-b ${cat.color} border border-white/40 hover:border-primary-200/50 hover:-translate-y-1 hover:shadow-card-hover liquid-glass glass-card`}
            style={{
              backdropFilter: 'blur(12px)',
              background: `linear-gradient(145deg, rgba(255,255,255,0.7), rgba(255,255,255,0.4))`,
            }}
          >
            <span className="block mb-1 group-hover:scale-110 transition-transform duration-300">{cat.icon}</span>
            <h3 className="text-sm font-bold text-primary-900">{cat.name}</h3>
            <p className="text-xs text-ink-muted mt-1 font-semibold">{cat.count} reports</p>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   FEATURED PROBLEMS CAROUSEL
   ═══════════════════════════════════════════════════════════════════ */
function FeaturedProblems() {
  const [offset, setOffset] = useState(0)
  const trackRef = useRef(null)
  const maxOffset = Math.max(0, PROBLEMS.length - 3)

  const prev = () => setOffset((p) => Math.max(0, p - 1))
  const next = () => setOffset((p) => Math.min(maxOffset, p + 1))

  return (
    <section className="section-container overflow-hidden" style={{ background: 'linear-gradient(180deg, #f0f5f1 0%, #e8f0ea 50%, #f0f5f1 100%)' }}>
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <span className="section-eyebrow reveal flex items-center gap-1.5"><div className="w-4 h-4">{Icons.Megaphone}</div> Featured</span>
          <h2 className="section-title reveal reveal-delay-1">Recently Reported Problems</h2>
          <p className="section-subtitle reveal reveal-delay-2">Real issues from citizens across Jharkhand, being solved through collaboration.</p>
        </div>
        <div className="flex gap-2 reveal">
          <button onClick={prev} disabled={offset === 0} className="carousel-nav-btn static translate-y-0 disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Previous">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <button onClick={next} disabled={offset >= maxOffset} className="carousel-nav-btn static translate-y-0 disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Next">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>

      <div className="feature-carousel-wrap mt-8 reveal reveal-delay-2">
        <div
          ref={trackRef}
          className="feature-carousel-track"
          style={{ transform: `translateX(-${offset * (100 / 3 + 1.5)}%)` }}
        >
          {PROBLEMS.map((p, i) => (
            <div key={i} className="feature-card liquid-glass glass-card">
              <div className="flex gap-2 flex-wrap">
                <span className={`card-tag ${p.tagClass}`}>{p.tag}</span>
                <span className="card-tag priority">{p.priority}</span>
              </div>
              <h3>{p.title}</h3>
              <p className="card-location">
                <svg className="w-3.5 h-3.5 text-ink-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                {p.location}
              </p>
              <div className="card-meta">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center text-xs font-bold text-primary-700">{p.team.charAt(0)}</div>
                  <div>
                    <div className="text-xs font-semibold text-primary-900">{p.team}</div>
                    <div className="text-[10px] text-ink-muted">{p.status}</div>
                  </div>
                </div>
                <button className="upvote-btn">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" /></svg>
                  {p.upvotes}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   HOW IT WORKS SECTION
   ═══════════════════════════════════════════════════════════════════ */
function HowItWorks() {
  return (
    <section id="how-it-works" className="section-container">
      <div className="text-center">
        <span className="section-eyebrow reveal flex items-center justify-center gap-1.5"><div className="w-4 h-4">{Icons.Process}</div> Process</span>
        <h2 className="section-title mx-auto reveal reveal-delay-1">How SICP Works</h2>
        <p className="section-subtitle mx-auto text-center reveal reveal-delay-2">From a local issue to lasting impact — a transparent, collaborative journey.</p>
      </div>

      <div className="how-it-works-grid">
        {STEPS.map((step, i) => (
          <div key={step.num} className={`how-step reveal reveal-delay-${Math.min(i + 1, 5)} liquid-glass glass-card p-6 rounded-2xl border border-white/40`}>
            <div className="how-step-number">{step.icon}</div>
            <h3>{step.title}</h3>
            <p>{step.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   IMPACT ANALYTICS SECTION (Dashboard-style)
   ═══════════════════════════════════════════════════════════════════ */
function ImpactAnalytics() {
  return (
    <section id="impact" className="section-container" style={{ background: 'linear-gradient(180deg, #f0f5f1 0%, #e8f0ea 50%, #f0f5f1 100%)' }}>
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <span className="section-eyebrow reveal flex items-center gap-1.5"><div className="w-4 h-4">{Icons.Chart}</div> Measurable Change</span>
          <h2 className="section-title reveal reveal-delay-1">Impact Analytics</h2>
          <p className="section-subtitle reveal reveal-delay-2">Track the impact we are creating together across Jharkhand.</p>
        </div>
        <div className="flex gap-2 reveal">
          <button className="px-3 py-1.5 rounded-lg text-xs font-bold border border-primary-200/40 text-primary-700 bg-white/60 backdrop-blur-sm">Jharkhand ▾</button>
          <button className="px-3 py-1.5 rounded-lg text-xs font-bold border border-primary-200/40 text-primary-700 bg-white/60 backdrop-blur-sm">This Year ▾</button>
        </div>
      </div>

      {/* Impact Stat Cards */}
      <div className="impact-grid reveal reveal-delay-2">
        {[
          { label: 'Problems Reported', value: '12,458', growth: '22%' },
          { label: 'Problems Resolved', value: '3,245', growth: '18%' },
          { label: 'People Impacted', value: '2.4M+', growth: '40%' },
          { label: 'Active Projects', value: '1,243', growth: '25%' },
        ].map((s) => (
          <div key={s.label} className="impact-stat-card liquid-glass glass-card">
            <div className="impact-label">{s.label}</div>
            <div className="impact-value"><AnimatedValue value={s.value} /></div>
            <div className="impact-growth">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" /></svg>
              {s.growth} from last year
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="analytics-panels reveal reveal-delay-3">
        {/* Donut Chart */}
        <div className="analytics-panel liquid-glass glass-card">
          <h3>Top Problem Categories</h3>
          <div className="flex items-start gap-6">
            <div className="donut-chart flex-shrink-0" />
            <ul className="legend-list mt-2">
              {[
                { label: 'Water & Sanitation', value: '32%', color: '#2563eb' },
                { label: 'Infrastructure', value: '24%', color: '#16a34a' },
                { label: 'Environment', value: '18%', color: '#eab308' },
                { label: 'Healthcare', value: '15%', color: '#dc2626' },
                { label: 'Education', value: '8%', color: '#7c3aed' },
                { label: 'Others', value: '3%', color: '#e5e7eb' },
              ].map((item) => (
                <li key={item.label} className="legend-item">
                  <span className="legend-dot" style={{ background: item.color }} />
                  {item.label}
                  <span className="legend-value">{item.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Map Panel */}
        <div className="analytics-panel liquid-glass glass-card">
          <h3>Problems by District</h3>
          <div className="mt-4 relative">
            <svg viewBox="0 0 260 170" className="w-full heatmap-svg" aria-label="Jharkhand heatmap">
              <path d="M61 17 96 8l28 16 38-5 23 24 35 14-10 30 18 30-28 24-11 34-37 11-29 25-37-18-33 14-25-29-33-7-5-33 16-27-1-34 29-7Z" />
              <circle cx="106" cy="79" r="15" style={{ color: '#ef4444' }} fill="currentColor" />
              <circle cx="170" cy="67" r="12" style={{ color: '#f59e0b' }} fill="currentColor" />
              <circle cx="127" cy="113" r="18" style={{ color: '#ef4444' }} fill="currentColor" />
              <circle cx="73" cy="116" r="9" style={{ color: '#22c55e' }} fill="currentColor" />
              <circle cx="194" cy="121" r="10" style={{ color: '#f59e0b' }} fill="currentColor" />
            </svg>
            <div className="flex justify-end items-center gap-2 mt-3 text-[11px] text-ink-muted">
              <span>Low</span>
              <div className="w-16 h-1.5 rounded-full bg-gradient-to-r from-emerald-300 via-amber-400 to-red-500" />
              <span>High</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   PROBLEM SHOWCASE (Submit + Detail preview side by side)
   ═══════════════════════════════════════════════════════════════════ */
function ProblemShowcase() {
  return (
    <section className="section-container">
      <div className="text-center mb-12">
        <span className="section-eyebrow reveal flex items-center justify-center gap-1.5"><div className="w-4 h-4">{Icons.Wrench}</div> Platform Preview</span>
        <h2 className="section-title mx-auto reveal reveal-delay-1">Submit & Track Problems</h2>
        <p className="section-subtitle mx-auto text-center reveal reveal-delay-2">An intuitive workflow from submission to resolution — built for everyone.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Submit a Problem Preview */}
        <div className="liquid-glass submit-preview reveal">
          <p className="section-eyebrow text-xs">Citizen Portal</p>
          <h3 className="text-xl font-bold text-primary-900 mt-2">Submit a Problem</h3>
          <p className="text-sm text-ink-muted mt-1">Help us understand the issue you are facing.</p>

          {/* Stepper */}
          <div className="stepper">
            <div className="stepper-step">
              <div className="stepper-number active">1</div>
              <div className="stepper-label">Problem Details</div>
            </div>
            <div className="stepper-line" />
            <div className="stepper-step">
              <div className="stepper-number">2</div>
              <div className="stepper-label">Add Evidence</div>
            </div>
            <div className="stepper-line" />
            <div className="stepper-step">
              <div className="stepper-number">3</div>
              <div className="stepper-label">Location</div>
            </div>
            <div className="stepper-line" />
            <div className="stepper-step">
              <div className="stepper-number">4</div>
              <div className="stepper-label">Review & Submit</div>
            </div>
          </div>

          <div className="form-field">
            <label>Problem Title <span className="required">*</span></label>
            <input placeholder="e.g. Potholes on Main Road, Harmu, Ranchi" readOnly />
          </div>
          <div className="form-field">
            <label>Problem Category <span className="required">*</span></label>
            <select defaultValue=""><option value="" disabled>Select Category</option></select>
          </div>
          <div className="form-field">
            <label>Description <span className="required">*</span></label>
            <textarea placeholder="Provide more details about the problem..." rows="3" readOnly />
          </div>
          <div className="form-field">
            <label>Who is affected?</label>
            <div className="radio-group">
              <label><input type="radio" name="affected" defaultChecked readOnly /> Community</label>
              <label><input type="radio" name="affected" readOnly /> Students</label>
              <label><input type="radio" name="affected" readOnly /> Environment</label>
              <label><input type="radio" name="affected" readOnly /> Other</label>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <button className="glass-btn glass-btn-secondary !text-sm !py-2 !px-5">Cancel</button>
            <button className="glass-btn glass-btn-primary !text-sm !py-2 !px-5">
              Next
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </button>
          </div>
        </div>

        {/* Problem Detail Preview */}
        <div className="liquid-glass problem-detail reveal reveal-delay-1">
          <button className="text-sm font-bold text-primary-600 hover:text-primary-800 transition-colors">← Back to Explore</button>

          <div className="problem-header mt-4">
            <div>
              <div className="problem-tags">
                <span className="tag-pill water">Water & Sanitation</span>
                <span className="tag-pill priority">High Priority</span>
              </div>
              <h2>Drinking Water Contamination in Hulhundu Village, Gumla</h2>
              <p className="problem-location">
                <div className="w-4 h-4 inline-block align-middle mr-1">{Icons.MapPin}</div>
                Hulhundu, Gumla, Jharkhand · Reported on 12 May 2025 by Ramesh H.
              </p>
            </div>
            <button className="upvote-badge">↑ Upvote <span>132</span></button>
          </div>

          <div className="detail-tabs">
            <button className="active">Details</button>
            <button>Evidence (4)</button>
            <button>Comments (8)</button>
            <button>Project Updates (3)</button>
          </div>

          <div className="detail-body">
            <div>
              <h4>Description</h4>
              <p>For the past two months, the drinking water has a foul smell and is causing health issues like stomach pain and skin rashes.</p>
              <h4>Category</h4>
              <p>Water & Sanitation · Drinking Water</p>
              <h4>Tags</h4>
              <p className="flex gap-2 flex-wrap">
                {['#water', '#contamination', '#rural', '#gumla'].map(t => (
                  <span key={t} className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">{t}</span>
                ))}
              </p>
              <h4>Status Timeline</h4>
              <ul className="status-timeline">
                <li className="done"><strong>Submitted</strong><span>12 May 2025</span></li>
                <li className="done"><strong>Validated</strong><span>15 May 2025</span></li>
                <li className="current"><strong>Routed to University</strong><span>NIT Jamshedpur · Civil Engg. Dept. · 20 May 2025</span></li>
                <li><strong>Pilot Testing</strong><span>Village Pilot in progress</span></li>
                <li><strong>Deployed</strong><span>Expected: 10 June 2025</span></li>
              </ul>
            </div>

            <div>
              <div className="detail-info-block">
                <h4>Assigned Team</h4>
                <div className="info-row">
                  <div className="info-avatar">N</div>
                  <div>
                    <p>NIT Jamshedpur</p>
                    <small>Civil Engineering Dept.</small>
                  </div>
                </div>
              </div>
              <div className="detail-info-block">
                <h4>Industry Partner</h4>
                <div className="info-row">
                  <div className="info-avatar" style={{ background: '#2563eb' }}>T</div>
                  <div>
                    <p>Tata Steel Foundation</p>
                    <small>CSR Partner</small>
                  </div>
                </div>
              </div>
              <div className="impact-estimate-box mt-3">
                <div className="ie-label">Estimated Impact</div>
                <div>
                  <div className="ie-value">2,500+</div>
                  <div className="ie-desc">People Benefiting</div>
                </div>
                <div>
                  <div className="ie-value">₹12 L</div>
                  <div className="ie-desc">CSR Funding</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   WHY SICP — FEATURE HIGHLIGHTS
   ═══════════════════════════════════════════════════════════════════ */
function WhySICP() {
  const features = [
    { icon: <div className="w-8 h-8 text-indigo-600">{Icons.Phone}</div>, title: 'Citizen Reporting', desc: 'Easy mobile-first reporting with photos, video evidence, and local-language support.' },
    { icon: <div className="w-8 h-8 text-blue-600">{Icons.AI}</div>, title: 'AI Smart Routing', desc: 'AI classifies, prioritises, and routes reports to the best-fit university experts.' },
    { icon: <div className="w-8 h-8 text-emerald-600">{Icons.Graduation}</div>, title: 'University Collaboration', desc: 'Connect with 18 universities across Jharkhand for innovative, research-backed solutions.' },
    { icon: <div className="w-8 h-8 text-rose-600">{Icons.Factory}</div>, title: 'Industry Partnership', desc: 'CSR funding, mentoring and real-world resources from 96 industry partners.' },
    { icon: <div className="w-8 h-8 text-amber-600">{Icons.MapPin}</div>, title: 'Project Tracking', desc: 'Transparent progress tracking from problem submission to deployed solution.' },
    { icon: <div className="w-8 h-8 text-cyan-600">{Icons.Chart}</div>, title: 'Impact Measurement', desc: 'Real-time dashboards measuring outcomes across every district of Jharkhand.' },
  ]

  return (
    <section className="section-container" id="about">
      <div className="text-center">
        <span className="section-eyebrow reveal flex items-center justify-center gap-1.5"><div className="w-4 h-4">{Icons.Sparkles}</div> Why Choose SICP</span>
        <h2 className="section-title mx-auto reveal reveal-delay-1">Built for Collaborative Impact</h2>
        <p className="section-subtitle mx-auto text-center reveal reveal-delay-2">A comprehensive platform designed to transform how Jharkhand solves its toughest challenges.</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5 mt-12">
        {features.map((f, i) => (
          <div
            key={f.title}
            className={`reveal reveal-delay-${Math.min(i + 1, 5)} group p-7 rounded-2xl cursor-default transition-all duration-300 hover:-translate-y-1 liquid-glass glass-card`}
            style={{
              background: 'rgba(255,255,255,0.55)',
              backdropFilter: 'blur(16px)',
              border: '1px solid rgba(255,255,255,0.5)',
              boxShadow: '0 4px 24px rgba(9,51,30,0.04)',
            }}
          >
            <span className="block mb-4 group-hover:scale-110 transition-transform duration-300">{f.icon}</span>
            <h3 className="text-lg font-bold text-primary-900">{f.title}</h3>
            <p className="text-sm text-ink-muted mt-2 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   PARTNERS SECTION
   ═══════════════════════════════════════════════════════════════════ */
function PartnersSection() {
  return (
    <section id="partners" className="section-container" style={{ background: 'linear-gradient(180deg, #f0f5f1 0%, #e8f0ea 50%, #f0f5f1 100%)' }}>
      <div className="text-center">
        <span className="section-eyebrow reveal flex items-center justify-center gap-1.5"><div className="w-4 h-4">{Icons.Handshake}</div> Collaboration Network</span>
        <h2 className="section-title mx-auto reveal reveal-delay-1">Our Partners in Jharkhand</h2>
        <p className="section-subtitle mx-auto text-center reveal reveal-delay-2">Universities and industries united for societal transformation.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-12 mt-12 relative">
        {/* Dim divider layout */}
        <div className="hidden md:block absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-transparent via-primary-200/50 to-transparent -translate-x-1/2" />
        
        {/* Universities */}
        <div className="reveal">
          <h3 className="text-sm font-bold text-primary-600 uppercase tracking-wider mb-6 text-center flex justify-center items-center gap-2">
            <div className="w-5 h-5">{Icons.Graduation}</div> University Partners
          </h3>
          <div className="partners-grid justify-center">
            {UNIVERSITY_PARTNERS.map((p) => (
              <div key={p.name} className="partner-logo liquid-glass glass-card">
                <span className="partner-icon block mb-2">{p.icon}</span>
                <span style={{ whiteSpace: 'pre-line' }}>{p.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Industry */}
        <div className="reveal reveal-delay-2">
          <h3 className="text-sm font-bold text-primary-600 uppercase tracking-wider mb-6 text-center flex justify-center items-center gap-2">
            <div className="w-5 h-5">{Icons.Factory}</div> Industry Partners
          </h3>
          <div className="partners-grid justify-center">
            {INDUSTRY_PARTNERS.map((p) => (
              <div key={p.name} className="partner-logo liquid-glass glass-card">
                <span className="partner-icon block mb-2">{p.icon}</span>
                <span style={{ whiteSpace: 'pre-line' }}>{p.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   CTA SECTION
   ═══════════════════════════════════════════════════════════════════ */
function CTASection() {
  return (
    <section className="section-container reveal">
      <div className="cta-section liquid-glass glass-card">
        <div className="orb orb-gold w-72 h-72 -top-20 -right-20 animate-float-slow" style={{ opacity: 0.15, filter: 'blur(40px)' }} />
        <div className="orb orb-blue w-56 h-56 -bottom-16 -left-16 animate-float" style={{ opacity: 0.1, filter: 'blur(40px)' }} />
        <h2>Join the Movement.<br />Shape Jharkhand's Future.</h2>
        <p>Be part of India's most ambitious collaborative problem-solving platform. Whether you're a citizen, student, researcher or industry leader — your contribution matters.</p>
        <div className="cta-buttons">
          <Link to="/citizen" className="cta-btn-white">
            Report a Problem
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </Link>
          <Link to="/university" className="cta-btn-outline">
            Partner With Us
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </Link>
        </div>
      </div>
    </section>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════════════════ */
function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-grid">
          <div className="footer-brand">
            <h3 className="flex items-center gap-3">
              <div className="bg-white/90 p-1.5 rounded-xl shadow-glass border border-white/20">
                <img src="/logo.jpg" alt="SICP Logo" className="h-8 w-auto mix-blend-multiply" style={{ mixBlendMode: 'multiply' }} />
              </div>
              <span className="font-extrabold text-xl tracking-tight">SICP</span>
            </h3>
            <p className="mt-5 text-white/80 leading-relaxed text-sm">Societal Innovation & Collaborative Portal — A Government of Jharkhand initiative connecting citizens, universities and industries to solve real-world challenges.</p>
            <div className="flex gap-3 mt-4">
              {['𝕏', 'in', 'fb', 'yt'].map(s => (
                <span key={s} className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-xs font-bold text-white/60 hover:bg-white/20 cursor-pointer transition-colors">{s}</span>
              ))}
            </div>
          </div>
          <div className="footer-col">
            <h4>Platform</h4>
            <a href="#explore">Explore Problems</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#impact">Impact Analytics</a>
            <a href="#partners">Partners</a>
          </div>
          <div className="footer-col">
            <h4>For Citizens</h4>
            <a href="#">Report a Problem</a>
            <a href="#">Track Submissions</a>
            <a href="#">Community Forum</a>
            <a href="#">Help & Support</a>
          </div>
          <div className="footer-col">
            <h4>For Institutions</h4>
            <a href="#">University Portal</a>
            <a href="#">Industry Partnership</a>
            <a href="#">Research Hub</a>
            <a href="#">API Documentation</a>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© 2025 SICP · Government of Jharkhand · All rights reserved</span>
          <div className="flex gap-4">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Accessibility</a>
          </div>
        </div>
        <div className="footer-hindi">समस्या आपकी, समाधान हमारा — मिलकर बनायें बेहतर झारखंड</div>
      </div>
    </footer>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   MAIN LANDING PAGE
   ═══════════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const pageRef = useReveal()

  return (
    <main ref={pageRef} className="overflow-x-hidden">
      <HeroSection />
      <StatsSection />
      <CategoriesSection />
      <FeaturedProblems />
      <HowItWorks />
      <WhySICP />
      <ProblemShowcase />
      <ImpactAnalytics />
      <PartnersSection />
      <CTASection />
      <Footer />
    </main>
  )
}
