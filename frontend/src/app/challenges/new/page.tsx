"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, classifierApi } from "@/lib/api";
import styles from "./page.module.css";
import { UploadCloud, Bot, MapPin, AlertTriangle, Send, Camera as CameraIcon } from "lucide-react";

import { supabase } from "@/lib/supabase";
import { Geolocation } from '@capacitor/geolocation';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';

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

  const takePhoto = async () => {
    try {
      const image = await Camera.getPhoto({
        quality: 80,
        allowEditing: false,
        resultType: CameraResultType.DataUrl,
        source: CameraSource.Camera // Forces the live camera
      });
      setPhoto(image.dataUrl || null);
    } catch (err) {
      console.error("Camera error:", err);
    }
  };

  const captureLocation = async () => {
    setLocationStatus("LOADING");
    try {
      const permissions = await Geolocation.checkPermissions();
      if (permissions.location !== 'granted') {
        await Geolocation.requestPermissions();
      }
      
      const position = await Geolocation.getCurrentPosition({ enableHighAccuracy: true });
      setFormData(prev => ({
        ...prev,
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      }));
      setLocationStatus("SUCCESS");
      setError("");
    } catch (err) {
      console.error("Location error:", err);
      setError("Location permission denied. It is compulsory to share your location.");
      setLocationStatus("ERROR");
    }
  };

  const [aiAnalysis, setAiAnalysis] = useState<any>(null);

  const analyzeWithAI = async () => {
    if (formData.narrative.length < 20) {
      setError("Please describe the issue in more detail (at least 20 characters).");
      return;
    }
    if (formData.latitude === null) {
      setError("Compulsory: Please capture your live location first.");
      return;
    }
    if (!photo) {
      setError("Compulsory: Please capture a live photo of the issue.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await classifierApi.post("/classify/full", {
        text: formData.narrative
      });
      setAiAnalysis(res.data);
      setFormData(prev => ({
        ...prev,
        domain: prev.domain || (res.data.predictions[0]?.domain) || DOMAINS[0],
        severity: res.data.severity || prev.severity,
        district: res.data.district_hint || prev.district
      }));
      setStep(2);
    } catch (err) {
      console.error(err);
      setError("AI analysis failed. Please select domain manually.");
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
                    <h3>Take Live Photo (Compulsory)</h3>
                    <p>Tap here to open your camera and snap the issue.</p>
                  </>
                )}
                {photo && (
                  <div className={styles.photoOverlay}>
                    <p>Tap to retake photo</p>
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
                disabled={loading || locationStatus !== 'SUCCESS'}
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
                      <span className={styles.aiValue}>{aiAnalysis.predictions[0]?.domain} ({(aiAnalysis.predictions[0]?.confidence * 100).toFixed(1)}%)</span>
                    </div>
                    <div className={styles.aiItem}>
                      <span className={styles.aiLabel}>Detected Severity:</span>
                      <span className={`${styles.aiValue} ${styles[aiAnalysis.severity?.toLowerCase() || '']}`}>{aiAnalysis.severity}</span>
                    </div>
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
