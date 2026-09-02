import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from '../i18n.jsx'

const PORTAL_LINKS = ['Dashboard', 'My Submissions', 'Track Projects', 'Explore Problems', 'Universities', 'Industry Partners', 'Community', 'Impact Analytics', 'Notifications', 'Help & Support']

const WHY_SICP = [
  ['▣', 'Citizen Reporting', 'Easy reporting with evidence, location & local-language support.'],
  ['⌘', 'AI Smart Routing', 'AI classifies, prioritises and routes reports to the best-fit experts.'],
  ['♜', 'University Collaboration', 'Connect with Jharkhand’s universities and colleges for innovative solutions.'],
  ['⌁', 'Industry Partnership', 'Bring CSR, mentoring and resources from industry partners.'],
  ['↗', 'Project Tracking', 'Track progress transparently from proposal to impact.'],
  ['◌', 'Impact Measurement', 'Measure real impact in communities across Jharkhand.'],
]

const ACTIVITY = [
  ['Your problem “Water leakage in 5th cross” has been validated.', 'Validated', 'green'],
  ['Project “Smart Waste Management” assigned to NIT Jamshedpur.', 'Routed', 'blue'],
  ['Your problem “Street light not working” is in progress.', 'In Progress', 'amber'],
  ['Thank you! Your upvote helped prioritize a community problem.', 'Upvoted', 'violet'],
]

const STEPS = [
  ['1.', 'Submit', 'Citizen submits a real-world problem'],
  ['2.', 'Validate', 'Community upvotes and moderator verifies'],
  ['3.', 'AI Process', 'AI classifies, prioritises and clusters'],
  ['4.', 'Route', 'Routed to the best matching university team'],
  ['5.', 'Collaborate', 'Solution proposed, funding and mentorship tracked'],
]

function Icon({ children, className = '' }) { return <span className={`mini-icon ${className}`}>{children}</span> }
function Arrow() { return <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14m-6-6 6 6-6 6" /></svg> }

export default function LandingPage() {
  const { lang } = useTranslation()
  const hi = lang === 'hi'

  return <main id="main-content" tabIndex="-1" className="sicp-canvas focus:outline-none">
    <div className="max-w-[1540px] mx-auto px-3 sm:px-4 py-3 sm:py-4">
      <section className="showcase-grid" aria-label="SICP overview">
        <section className="hero-showcase glass-card" aria-labelledby="hero-heading">
          <div className="hero-copy">
            <p className="eyebrow">SOCIETAL INNOVATION &amp; COLLABORATIVE PORTAL</p>
            <h1 id="hero-heading">{hi ? 'वास्तविक समस्याओं का समाधान। बेहतर झारखंड का निर्माण।' : <>Solving Real Problems.<br />Building a Better<br /><span>Jharkhand</span> Together.</>}</h1>
            <p>{hi ? 'SICP नागरिकों, विश्वविद्यालयों और उद्योगों को झारखंड में वास्तविक चुनौतियों पर सहयोग करने के लिए जोड़ता है।' : 'SICP connects citizens, universities and industry to collaborate on real-world challenges across Jharkhand.'}</p>
            <div className="flex flex-wrap gap-2.5 mt-5"><Link to="/citizen" className="portal-button">Report a Problem <Arrow /></Link><Link to="/citizen/tracker" className="portal-button portal-button-light">Explore Problems <Arrow /></Link></div>
          </div>
          <div className="jharkhand-scene" aria-hidden="true">
            <svg viewBox="0 0 530 335" className="jharkhand-map"><path d="M130 39 188 22l43 19 55-7 36 27 50 17-9 44 28 44-35 29-16 50-57 20-39 36-61-18-45 19-38-34-45-11-10-49 22-46-3-51 45-11Z" /><path className="map-route" d="M175 87c35 27 77 48 132 41 46-6 52 45 37 101" /></svg>
            <MapPin style={{ left: '39%', top: '40%' }} label="Ranchi" /><MapPin style={{ left: '68%', top: '34%' }} label="Bokaro" /><MapPin style={{ left: '53%', top: '62%' }} label="Jamshedpur" />
            <div className="scene-hills" /><div className="scene-water" /><div className="scene-people"><i /><i /><i /><i /></div>
          </div>
          <div className="hero-stats">{[['▧', 'Problems Reported', '12,458'], ['♧', 'Active Projects', '1,243'], ['♜', 'Universities', '18'], ['⌂', 'Industry Partners', '96'], ['♙', 'People Impacted', '2.4M+']].map(([icon, label, value]) => <div key={label}><Icon>{icon}</Icon><span>{label}</span><strong>{value}</strong></div>)}</div>
        </section>

        <aside className="portal-rail glass-card" aria-label="SICP portal navigation">
          <div className="rail-brand blend-logo"><img src="/sicp-jharkhand-logo.jpeg" alt="Government of Jharkhand and SICP" /></div>
          <nav>{PORTAL_LINKS.map((link, index) => <Link key={link} to={index === 0 ? '/' : index === 1 ? '/citizen/tracker' : index === 7 ? '/admin' : '/university'} className={index === 0 ? 'active' : ''}><Icon>{['⌂', '□', '⌁', '⌕', '♜', '♧', '♙', '↗', '◌', '?'][index]}</Icon><span>{link}</span></Link>)}</nav>
        </aside>

        <section className="welcome-panel glass-card" aria-labelledby="welcome-heading">
          <div className="welcome-bar"><div><p className="eyebrow">SICP PORTAL</p><h2 id="welcome-heading">Welcome back, Kashvi! <span aria-hidden="true">👋</span></h2></div><div className="portal-search">⌕ <span>Search problems, projects, people...</span></div><div className="avatar">K</div></div>
          <div className="status-cards">{[['My Submissions', '3', 'blue'], ['In Progress', '2', 'amber'], ['Resolved', '1', 'green'], ['Upvoted by Me', '5', 'violet']].map(([label, value, color]) => <div className={`status-card ${color}`} key={label}><span>{label}</span><strong>{value}</strong><small>View all</small></div>)}</div>
          <div className="dashboard-split">
            <div className="activity-panel"><div className="panel-heading"><h3>Recent Activity</h3><button>View all</button></div>{ACTIVITY.map(([text, tag, color]) => <div className="activity-row" key={text}><Icon className={color}>◉</Icon><p>{text}<small>2h ago</small></p><b className={color}>{tag}</b></div>)}</div>
            <div className="heatmap-panel"><div className="panel-heading"><h3>Jharkhand Problem Heatmap</h3><button>District View⌄</button></div><Heatmap /><div className="heat-legend"><span>Low</span><i /><span>High</span></div></div>
          </div>
        </section>

        <aside className="why-panel glass-card" id="about"><h2>Why SICP?</h2>{WHY_SICP.map(([icon, title, text]) => <div className="why-item" key={title}><Icon>{icon}</Icon><div><h3>{title}</h3><p>{text}</p></div></div>)}<div className="jharkhand-sign">जोहार झारखंड</div></aside>
      </section>

      <section id="explore" className="operations-grid scroll-mt-24" aria-label="SICP operations">
        <article className="submission-card glass-card"><div className="panel-heading"><div><p className="eyebrow">CITIZEN PORTAL</p><h2>Submit a Problem</h2><p>Help us understand the issue you are facing.</p></div></div><div className="stepper"><b>1<br /><small>Problem Details</small></b><span /><b>2<br /><small>Add Evidence</small></b><span /><b>3<br /><small>Location</small></b><span /><b>4<br /><small>Review &amp; Submit</small></b></div><label>Problem Title <em>*</em><input placeholder="e.g. Potholes on Main Road, Harmu, Ranchi" /></label><label>Problem Category <em>*</em><select defaultValue=""><option value="" disabled>Select Category</option><option>Water Management</option><option>Sanitation</option><option>Healthcare</option></select></label><label>Description <em>*</em><textarea placeholder="Provide more details about the problem..." rows="3" /><small>0/500</small></label><fieldset><legend>Who is affected?</legend><label><input type="radio" name="affected" defaultChecked /> Community</label><label><input type="radio" name="affected" /> Students</label><label><input type="radio" name="affected" /> Environment</label><label><input type="radio" name="affected" /> Other</label></fieldset><div className="form-actions"><button>Cancel</button><Link to="/citizen" className="portal-button">Next <Arrow /></Link></div></article>

        <article className="detail-card glass-card"><Link to="/citizen/tracker" className="back-link">← Back to Explore</Link><div className="detail-top"><div><div className="flex gap-2"><span className="tag aqua">Water &amp; Sanitation</span><span className="tag red">High Priority</span></div><h2>Drinking Water Contamination in Hulhundu Village, Gumla</h2><p>⌖ Hulhundu, Gumla, Jharkhand &nbsp; · &nbsp; Reported on 12 May 2025 by Ramesh H.</p></div><button className="upvote">↑ Upvote <b>132</b></button></div><div className="tabs"><b>Details</b><span>Evidence (4)</span><span>Comments (8)</span><span>Project Updates (3)</span></div><div className="detail-content"><div><h3>Description</h3><p>For the past two months, the drinking water has a foul smell and is causing health issues like stomach pain and skin rashes.</p><h3>Category</h3><p>Water &amp; Sanitation · Drinking Water</p><h3>Tags</h3><p>#water &nbsp; #contamination &nbsp; #rural &nbsp; #gumla</p><h3>Status Timeline</h3><ol className="timeline"><li className="done"><b>Submitted</b><span>12 May 2025</span></li><li className="done"><b>Validated</b><span>15 May 2025</span></li><li className="current"><b>Routed to University</b><span>20 May 2025 · NIT Jamshedpur</span></li><li><b>Pilot Testing</b><span>May–June 2025</span></li><li><b>Deployed</b><span>Expected June 2025</span></li></ol></div><div className="partner-stack"><InfoBlock title="Assigned Team" body="NIT Jamshedpur · Civil Engineering Dept." /><InfoBlock title="Industry Partner" body="Tata Steel Foundation · CSR Partner" /><div className="impact-estimate"><small>Estimated Impact</small><strong>2,500+</strong><span>people impacted</span><strong>₹12 L</strong><span>CSR funding</span></div></div></div></article>

        <article className="analytics-card glass-card" id="impact"><div className="panel-heading"><div><p className="eyebrow">MEASURABLE CHANGE</p><h2>Impact Analytics</h2><p>Track the impact we are creating together.</p></div><div className="filter-pills"><button>Jharkhand⌄</button><button>This Year⌄</button></div></div><div className="impact-cards">{[['Problems Reported', '12,458', '22%'], ['Problems Resolved', '3,243', '18%'], ['People Impacted', '2.4M+', '40%'], ['Active Projects', '1,243', '25%']].map(([label, value, growth]) => <div key={label}><span>{label}</span><strong>{value}</strong><small>↗ {growth} from last year</small></div>)}</div><div className="charts"><div><h3>Top Problem Categories</h3><div className="donut" /><ul><li><i className="blue" /> Water &amp; Sanitation <b>32%</b></li><li><i className="green" /> Infrastructure <b>24%</b></li><li><i className="gold" /> Environment <b>18%</b></li><li><i className="red" /> Healthcare <b>15%</b></li><li><i className="purple" /> Education <b>8%</b></li></ul></div><div><h3>Problems by District</h3><Heatmap muted /></div></div></article>
      </section>

      <section id="how-it-works" className="how-strip glass-card scroll-mt-24"><div><p className="eyebrow">HOW IT WORKS</p><h2>From a local issue to lasting impact.</h2></div><div className="how-steps">{STEPS.map(([number, title, text]) => <div key={title}><Icon>{number}</Icon><h3>{title}</h3><p>{text}</p></div>)}</div></section>

      <section className="ecosystem-strip glass-card"><div><div><p className="eyebrow">COLLABORATION NETWORK</p><h2>Our Partners in Jharkhand</h2><div className="partner-logos"><span>NIT<br />Jamshedpur</span><span>XLRI<br />Jamshedpur</span><span>BIT<br />Mesra</span><span>Ranchi<br />University</span><span>Tata Steel<br />Foundation</span></div></div><div><p className="eyebrow">BUILT FOR SCALE</p><h2>Tech Stack</h2><div className="tech-logos"><span>⚛<b>React JS</b></span><span>⬡<b>Node.js</b></span><span>⌘<b>Python</b></span><span>◫<b>PostgreSQL</b></span><span>☁<b>AWS</b></span><span>✣<b>NLP &amp; ML</b></span></div></div></div></section>
      <div className="jharkhand-footerline">समस्या आपकी, समाधान हमारा — मिलकर बनायें बेहतर झारखंड</div>
    </div>
  </main>
}

function MapPin({ style, label }) { return <span className="map-pin" style={style}><i>●</i><b>{label}</b></span> }

function Heatmap({ muted = false }) { return <div className={`heatmap ${muted ? 'muted' : ''}`}><svg viewBox="0 0 260 170" aria-label="Jharkhand heatmap"><path d="M61 17 96 8l28 16 38-5 23 24 35 14-10 30 18 30-28 24-11 34-37 11-29 25-37-18-33 14-25-29-33-7-5-33 16-27-1-34 29-7Z" /><circle cx="106" cy="79" r="15" /><circle cx="170" cy="67" r="12" /><circle cx="127" cy="113" r="18" /><circle cx="73" cy="116" r="9" /><circle cx="194" cy="121" r="10" /></svg></div> }

function InfoBlock({ title, body }) { return <div className="info-block"><h3>{title}</h3><div><span className="team-avatar">N</span><p>{body}<small>View details →</small></p></div></div> }
