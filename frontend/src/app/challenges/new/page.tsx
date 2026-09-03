"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api, classifierApi } from "@/lib/api";
import styles from "./page.module.css";
import { UploadCloud, Bot, MapPin, AlertTriangle, Send, Camera as CameraIcon } from "lucide-react";

import { supabase } from "@/lib/supabase";
// Capacitor plugins are only available inside the native Android/iOS shell.
// On web we use the standard browser APIs instead (navigator.geolocation +
// <input type="file" capture="environment">).

const DOMAINS = [
  "Education", "Agriculture", "Healthcare", "Water Resources", 
  "Environment", "Energy", "Urban Development", "Accessibility", 
  "Public Administration", "Rural Livelihoods"
];

export default function SubmitChallenge() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    title: "",
    narrative: "",
    domain: "",
    severity: "MEDIUM",
    district: "",
    is_anonymous: false,
    proposed_solution: "",
    latitude: null as number | null,
    longitude: null as number | null,
  });

  const [locationStatus, setLocationStatus] = useState<"IDLE" | "LOADING" | "SUCCESS" | "ERROR">("IDLE");

  const [photo, setPhoto] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Works on all browsers: opens native camera on mobile, file picker on desktop.
  const takePhoto = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setPhoto(reader.result as string);
    reader.readAsDataURL(file);
  };

  // Uses the standard browser Geolocation API — works on web, Android, and iOS.
  const captureLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      setLocationStatus("ERROR");
      return;
    }
    setLocationStatus("LOADING");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData(prev => ({
          ...prev,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        }));
        setLocationStatus("SUCCESS");
        setError("");
      },
      (err) => {
        console.error("Location error:", err);
        setError(
          err.code === err.PERMISSION_DENIED
            ? "Location permission denied. Please allow location access in your browser settings."
            : "Could not get location. Please try again."
        );
        setLocationStatus("ERROR");
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  };

  const [aiAnalysis, setAiAnalysis] = useState<any>(null);

  const analyzeWithAI = async () => {
    if (formData.narrative.length < 20) {
      setError("Please describe the issue in more detail (at least 20 characters).");
      return;
    }
    if (formData.latitude === null) {
      setError("Please capture your location first.");
      return;
    }
    // Photo is encouraged but not a hard blocker on web.
    setError("");
    setLoading(true);
    try {
      const res = await classifierApi.post("/classify/full", {
        text: formData.narrative,
        lat: formData.latitude,
        lng: formData.longitude,
      });
      const d = res.data;
      setAiAnalysis(d);
      // /classify/full returns: domain, top_3_predictions, severity_boost,
      // geo_validation.district_hint — map these to formData.
      setFormData(prev => ({
        ...prev,
        domain: prev.domain || d.domain || DOMAINS[0],
        district: prev.district || d.geo_validation?.district_hint || "",
      }));
      setStep(2);
    } catch (err) {
      console.error(err);
      // AI server not running is not fatal — let user fill manually.
      setError("AI server unreachable. You can still fill the form manually below.");
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data, error: sbError } = await supabase
        .from('challenges')
        .insert([formData])
        .select();

      if (sbError) throw sbError;
      
      if (data && data.length > 0) {
        router.push(`/dashboard`); // Go back to dashboard to see realtime in action!
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to submit challenge to Supabase.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>Submit a Grievance</h1>
          <p>Report an issue in your community for student innovators to solve.</p>
        </div>

        <div className={styles.stepper}>
          <div className={`${styles.step} ${step >= 1 ? styles.active : ""}`}>1. Details</div>
          <div className={styles.stepLine} />
          <div className={`${styles.step} ${step >= 2 ? styles.active : ""}`}>2. Review & Submit</div>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          {step === 1 && (
            <div className={styles.stepContent}>

              {/* Hidden file input — triggered by the upload zone click */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                style={{ display: "none" }}
                onChange={handleFileChange}
              />

              <div
                className={`${styles.uploadZone} ${photo ? styles.hasPhoto : ''}`}
                onClick={takePhoto}
                style={{ backgroundImage: photo ? `url(${photo})` : 'none', backgroundSize: 'cover', backgroundPosition: 'center' }}
              >
                {!photo && (
                  <>
                    <div className={styles.uploadIconWrapper}>
                      <CameraIcon size={48} />
                    </div>
                    <h3>Take Photo / Upload Image</h3>
                    <p>Tap to open your camera or choose a file from your device.</p>
                  </>
                )}
                {photo && (
                  <div className={styles.photoOverlay}>
                    <p>Tap to retake / change photo</p>
                  </div>
                )}
              </div>

              <div className={styles.inputGroup}>
                <label>Title</label>
                <input 
                  type="text" 
                  placeholder="E.g. Frequent flooding in sector 4 during monsoons"
                  value={formData.title}
                  onChange={e => setFormData({...formData, title: e.target.value})}
                  required
                  minLength={10}
                />
              </div>
              <div className={styles.inputGroup}>
                <label>Detailed Description</label>
                <textarea 
                  rows={6}
                  placeholder="Describe the problem, who it affects, and how long it has been happening..."
                  value={formData.narrative}
                  onChange={e => setFormData({...formData, narrative: e.target.value})}
                  required
                  minLength={20}
                />
              </div>

              <div className={styles.locationZone}>
                <button 
                  type="button"
                  className={`${styles.locationBtn} ${locationStatus === 'SUCCESS' ? styles.locSuccess : ''}`}
                  onClick={captureLocation}
                >
                  <MapPin size={18} />
                  {locationStatus === 'IDLE' && "Capture Live Location (Compulsory)"}
                  {locationStatus === 'LOADING' && "Locating..."}
                  {locationStatus === 'SUCCESS' && `Location Verified: ${formData.latitude?.toFixed(4)}, ${formData.longitude?.toFixed(4)}`}
                  {locationStatus === 'ERROR' && "Failed. Try Again."}
                </button>
              </div>
              
              <button
                type="button"
                className={styles.nextBtn}
                onClick={analyzeWithAI}
                disabled={loading || locationStatus === 'LOADING'}
              >
                <Bot size={18} /> {loading ? "Analyzing..." : "Next: AI Analysis"}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className={styles.stepContent}>
              
              {aiAnalysis && (
                <div className={styles.aiPanel}>
                  <div className={styles.aiHeader}>
                    <Bot size={20} /> AI Analysis Results
                  </div>
                  <div className={styles.aiGrid}>
                    <div className={styles.aiItem}>
                      <span className={styles.aiLabel}>Suggested Domain:</span>
                      <span className={styles.aiValue}>
                        {aiAnalysis.domain}
                        {aiAnalysis.confidence != null && ` (${(aiAnalysis.confidence * 100).toFixed(1)}%)`}
                      </span>
                    </div>
                    <div className={styles.aiItem}>
                      <span className={styles.aiLabel}>Priority Score:</span>
                      <span className={styles.aiValue}>{aiAnalysis.priority_score?.toFixed(1) ?? "—"}</span>
                    </div>
                    <div className={styles.aiItem}>
                      <span className={styles.aiLabel}>Classifier Method:</span>
                      <span className={styles.aiValue}>{aiAnalysis.method ?? "—"}</span>
                    </div>
                    {aiAnalysis.geo_validation?.district_hint && (
                      <div className={styles.aiItem}>
                        <span className={styles.aiLabel}>District Detected:</span>
                        <span className={styles.aiValue}>{aiAnalysis.geo_validation.district_hint}</span>
                      </div>
                    )}
                    {aiAnalysis.is_spam && (
                      <div className={styles.spamAlert}>
                        <AlertTriangle size={16} /> Possible Spam Detected. Your submission will be reviewed.
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className={styles.inputRow}>
                <div className={styles.inputGroup}>
                  <label>Domain</label>
                  <select 
                    value={formData.domain}
                    onChange={e => setFormData({...formData, domain: e.target.value})}
                    required
                  >
                    <option value="">Select Domain...</option>
                    {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
                <div className={styles.inputGroup}>
                  <label>Severity</label>
                  <select 
                    value={formData.severity}
                    onChange={e => setFormData({...formData, severity: e.target.value})}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label>District (Jharkhand)</label>
                <input 
                  type="text" 
                  placeholder="E.g. Ranchi, Dhanbad..."
                  value={formData.district}
                  onChange={e => setFormData({...formData, district: e.target.value})}
                />
              </div>

              <div className={styles.inputGroup}>
                <label>Probable Solution (Optional)</label>
                <textarea 
                  value={formData.proposed_solution}
                  onChange={(e) => setFormData({...formData, proposed_solution: e.target.value})}
                  className={styles.textarea}
                  placeholder="How do you think this could be solved? (e.g., Replace the damaged valve at the junction)"
                />
              </div>

              <div className={styles.checkboxGroup}>
                <input 
                  type="checkbox" 
                  id="anon"
                  checked={formData.is_anonymous}
                  onChange={e => setFormData({...formData, is_anonymous: e.target.checked})}
                />
                <label htmlFor="anon">Submit anonymously</label>
              </div>

              <div className={styles.actionRow}>
                <button type="button" className={styles.backBtn} onClick={() => setStep(1)}>
                  Back
                </button>
                <button type="submit" className={styles.submitBtn} disabled={loading}>
                  {loading ? "Submitting..." : <><Send size={18} /> Submit Challenge</>}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
