import React, { useState, useEffect, useRef } from 'react';
import { 
  Camera, Upload, FileText, CheckCircle2, AlertTriangle, XCircle, 
  Layers, Search, ShieldCheck, Scale, Cpu, Activity, RefreshCw, 
  Eye, Download, BarChart2, Zap
} from 'lucide-react';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export default function App() {
  const [activeTab, setActiveTab] = useState('inspection');
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  
  // Estados de cámara e imagen
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [currentImageBase64, setCurrentImageBase64] = useState(null);
  const [rectifyPerspective, setRectifyPerspective] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [validationError, setValidationError] = useState(null);

  const [signatureTabMode, setSignatureTabMode] = useState('document'); // 'document' | 'dual'
  const [dualComparisonResults, setDualComparisonResults] = useState(null);
  const [isComparingDual, setIsComparingDual] = useState(false);

  const [videoDevices, setVideoDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  // Cargar muestras y benchmarks al iniciar
  useEffect(() => {
    fetch(`${API_BASE}/api/samples`)
      .then(res => res.json())
      .then(data => {
        if (data.samples && data.samples.length > 0) {
          setSamples(data.samples);
          // Cargar primera muestra por defecto
          setSelectedSample(data.samples[0].id);
          setCurrentImageBase64(data.samples[0].image_base64);
        }
      })
      .catch(err => console.error("Error al cargar muestras:", err));

    fetch(`${API_BASE}/api/benchmark/models`)
      .then(res => res.json())
      .then(data => setBenchmarkData(data))
      .catch(err => console.error("Error al cargar benchmarks:", err));
  }, []);

  // Manejador de cámara web con soporte para selección de dispositivo (Laptop vs Celular) y fallback tolerante
  const startCamera = async (targetDeviceId = null) => {
    try {
      setIsCameraActive(true);
      const devId = targetDeviceId || selectedDeviceId;
      
      let stream = null;
      // Intento 1: Con dispositivo específico si fue elegido o con resolución estándar
      try {
        const constraints = devId 
          ? { video: { deviceId: { exact: devId } } }
          : { video: { width: { ideal: 1280 }, height: { ideal: 720 } } };
        stream = await navigator.mediaDevices.getUserMedia(constraints);
      } catch (err1) {
        console.warn("Intento 1 falló, probando con video universal:", err1);
        // Intento 2: Universal sin restricciones estrictas
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      // Enumerar cámaras disponibles (ej. Iriun Webcam, DroidCam o Cámara Integrada)
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputs = devices.filter(d => d.kind === 'videoinput');
        setVideoDevices(videoInputs);
        if (!selectedDeviceId && videoInputs.length > 0) {
          const currentTrack = stream.getVideoTracks()[0];
          const currentSettings = currentTrack ? currentTrack.getSettings() : null;
          setSelectedDeviceId(currentSettings?.deviceId || videoInputs[0].deviceId);
        }
      } catch (e) {
        console.log("No se pudieron enumerar los dispositivos:", e);
      }
    } catch (err) {
      console.error("No se pudo acceder a la cámara:", err);
      let msg = "No se pudo acceder a la cámara.";
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = "Permisos de cámara bloqueados en el navegador. Haz clic en el ícono del candado o cámara junto a 'localhost:5173' en la barra de direcciones y selecciona 'Permitir'.";
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        msg = "La cámara está ocupada por otra aplicación o Iriun no está conectado aún a tu celular. Asegúrate de tener la app de Iriun abierta en el teléfono y en la PC.";
      } else {
        msg = `Error al abrir cámara (${err.name || 'Desconocido'}): ${err.message || 'Verifica la conexión'}.`;
      }
      alert(msg);
      setIsCameraActive(false);
    }
  };


  const handleDeviceChange = (e) => {
    const newId = e.target.value;
    setSelectedDeviceId(newId);
    stopCamera();
    setTimeout(() => startCamera(newId), 200);
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };


  const captureCameraFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 800;
    canvas.height = videoRef.current.videoHeight || 600;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const b64 = canvas.toDataURL('image/png');
    setCurrentImageBase64(b64);
    setSelectedSample('camera');
    setValidationError(null);
    setAnalysisResults(null);
    stopCamera();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (uploadEvent) => {
        setCurrentImageBase64(uploadEvent.target.result);
        setSelectedSample('upload');
        setValidationError(null);
        setAnalysisResults(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const runDualComparison = async () => {
    if (!currentImageBase64) return;
    setIsComparingDual(true);
    try {
      const res = await fetch(`${API_BASE}/api/signatures/compare_dual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: currentImageBase64 })
      });
      const data = await res.json();
      setDualComparisonResults(data);
    } catch (err) {
      console.error("Error en cotejo dual:", err);
      alert("Ocurrió un error al ejecutar el cotejo dual.");
    } finally {
      setIsComparingDual(false);
    }
  };

  const handleSelectSample = (sampleId) => {
    const sample = samples.find(s => s.id === sampleId);
    if (sample) {
      setSelectedSample(sample.id);
      setCurrentImageBase64(sample.image_base64);
      setAnalysisResults(null);
      setValidationError(null);
      stopCamera();
    }
  };

  // Ejecutar Peritaje Forense Completo
  const runFullAnalysis = async () => {
    if (!currentImageBase64) {
      alert("Por favor captura o sube una imagen de documento primero.");
      return;
    }
    setIsAnalyzing(true);
    setValidationError(null);
    try {
      const response = await fetch(`${API_BASE}/api/analyze/full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: currentImageBase64,
          rectify_perspective: rectifyPerspective
        })
      });
      const data = await response.json();
      if (data.success) {
        setAnalysisResults(data);
        setValidationError(null);
      } else {
        setValidationError(data);
        setAnalysisResults(null);
      }
    } catch (err) {
      console.error("Error en peritaje:", err);
      alert("Error de conexión con el servidor forense.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const inks = analysisResults?.inks_analysis;
  const tampering = analysisResults?.tampering_analysis;
  const signature = analysisResults?.signature_analysis;
  const chronology = analysisResults?.chronology_analysis;
  const report = analysisResults?.judicial_report;

  return (
    <div className="min-h-screen bg-[#F8F6F0] text-[#292524] flex flex-col selection:bg-[#E5DFD3] selection:text-[#1C1917]">
      {/* HEADER SUPERIOR */}
      <header className="border-b border-[#E5E0D6] bg-white/85 backdrop-blur-md px-6 py-4 sticky top-0 z-50 flex items-center justify-between shadow-[0_1px_3px_rgba(0,0,0,0.02)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#292524] flex items-center justify-center shadow-sm">
            <Scale className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xl font-bold tracking-wider text-[#1C1917]">Docu<span className="text-[#8B5E3C]">CSI</span></span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#EFECE6] text-[#8B5E3C] border border-[#DDD7CC]">IA Neuro-Simbólica</span>
            </div>
            <p className="text-xs text-[#78716C]">Suite Forense de Documentoscopía, Espectrometría y Verificación Pericial</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-[#78716C]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Motor IA: <strong className="text-[#1C1917]">PyTorch + Scikit-Learn + A*</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#8B5E3C]" />
            <span>Cadena de Custodia: <strong className="text-[#1C1917]">SHA-256 Activa</strong></span>
          </div>
        </div>
      </header>

      {/* BARRA DE CAPTURA Y MUESTRAS RÁPIDAS */}
      <section className="bg-[#EFECE6] border-b border-[#E2DDD3] px-6 py-2.5">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button 
              onClick={isCameraActive ? stopCamera : startCamera}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                isCameraActive 
                  ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30' 
                  : 'bg-[#292524] hover:bg-[#3F3A36] text-[#FAF8F5] font-medium shadow-sm'
              }`}
            >
              <Camera className="w-4 h-4" />
              {isCameraActive ? 'Detener Cámara' : 'Cámara en Vivo'}
            </button>

            <button 
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium bg-white hover:bg-[#F5F2EC] text-[#292524] border border-[#DDD7CD] shadow-sm transition-all"
            >
              <Upload className="w-4 h-4" />
              Subir Imagen
            </button>
            <input 
              ref={fileInputRef} 
              type="file" 
              accept="image/*" 
              className="hidden" 
              onChange={handleFileUpload} 
            />

            <label className="flex items-center gap-2 text-xs text-[#44403C] ml-2 cursor-pointer select-none">
              <input 
                type="checkbox" 
                checked={rectifyPerspective} 
                onChange={(e) => setRectifyPerspective(e.target.checked)}
                className="rounded bg-white border-[#DDD7CD] text-[#8B5E3C] focus:ring-0"
              />
              Auto-Rectificación de Perspectiva (Homografía)
            </label>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto">
            <span className="text-xs text-[#78716C] uppercase tracking-wider font-semibold mr-1">Casos Simulados:</span>
            {samples.map(s => (
              <button
                key={s.id}
                onClick={() => handleSelectSample(s.id)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                  selectedSample === s.id 
                    ? 'bg-[#292524] text-[#FAF8F5] font-semibold shadow-sm' 
                    : 'bg-white hover:bg-[#F5F2EB] text-[#57534E] border border-[#DDD7CD]'
                }`}
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* VISTA DE CÁMARA ACTIVA (SI ESTÁ ENCENDIDA) */}
      {isCameraActive && (
        <div className="bg-[#EAE5DB] border-b border-[#D8D1C3] p-6 flex flex-col items-center">
          <div className="relative rounded-xl overflow-hidden border-2 border-emerald-500 shadow-2xl shadow-emerald-500/25 max-w-2xl w-full">
            <video ref={videoRef} autoPlay playsInline className="w-full h-auto bg-black" />
            <div className="absolute inset-0 pointer-events-none border border-[#8B5E3C]/40 m-6 rounded-lg flex items-center justify-center">
              <div className="border border-dashed border-[#8B5E3C]/60 w-4/5 h-3/5 rounded flex items-center justify-center">
                <span className="text-xs font-mono text-[#FAF8F5] bg-[#1C1917]/80 px-2 py-1 rounded">Enfoca el documento dentro del marco</span>
              </div>
            </div>

            {/* SELECTOR DE CÁMARA (PC vs CELULAR IRIUN / DROIDCAM) */}
            {videoDevices.length > 1 && (
              <div className="absolute top-3 right-3 flex items-center gap-2 bg-[#FAF9F5]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-emerald-500/50 shadow-lg">
                <Camera className="w-3.5 h-3.5 text-[#8B5E3C]" />
                <select 
                  value={selectedDeviceId}
                  onChange={handleDeviceChange}
                  className="bg-transparent text-[#8B5E3C] text-xs font-medium focus:outline-none cursor-pointer max-w-[200px] truncate"
                >
                  {videoDevices.map((dev, idx) => (
                    <option key={dev.deviceId || idx} value={dev.deviceId} className="bg-[#F5F2EB] text-[#292524]">
                      {dev.label || `Cámara ${idx + 1}`}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-3">
              <button 
                onClick={captureCameraFrame}
                className="px-6 py-2.5 rounded-full bg-emerald-500 hover:bg-[#8B5E3C] text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/40 flex items-center gap-2 transition-all cursor-pointer"
              >
                <Camera className="w-4 h-4" /> Capturar Documento para Peritaje
              </button>
              <button 
                onClick={stopCamera}
                className="px-4 py-2 rounded-full bg-[#F5F2EB]/90 hover:bg-[#EFECE6] text-[#44403C] text-xs border border-[#D8D1C3] transition-all cursor-pointer"
              >
                Cancelar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* CONTENIDO PRINCIPAL */}
      <main className="max-w-7xl w-full mx-auto p-6 flex-1 flex flex-col gap-6">
        
        {/* BARRA DE NAVEGACIÓN POR PESTAÑAS (MÓDULOS DEL SÍLABO) */}
        <nav className="flex flex-wrap gap-2 border-b border-[#E2DDD3] pb-2">
          {[
            { id: 'inspection', label: '1. Inspección & Visión', icon: Eye },
            { id: 'inks', label: '2. Espectro de Tintas (No Supervisado)', icon: Layers },
            { id: 'tampering', label: '3. Adulteración de Cifras (Supervisado)', icon: Search },
            { id: 'signature', label: '4. Firma & Dinámica Motora (Deep Learning)', icon: Activity },
            { id: 'chronology', label: '5. Cruce de Trazos (A*)', icon: Cpu },
            { id: 'report', label: '6. Dictamen Judicial (Sistema Experto)', icon: FileText },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-white text-[#1C1917] border-b-2 border-[#1C1917] shadow-sm font-semibold' 
                    : 'text-[#78716C] hover:text-[#1C1917] hover:bg-[#EFECE6]'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#8B5E3C]' : 'text-[#A8A29E]'}`} />
                {tab.label}
              </button>
            );
          })}

          <div className="ml-auto">
            <button
              onClick={runFullAnalysis}
              disabled={isAnalyzing || !currentImageBase64}
              className="flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm bg-[#1C1917] hover:bg-[#38332F] text-[#FAF8F5] shadow-sm disabled:opacity-50 transition-all cursor-pointer"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Ejecutando Peritaje Multi-Módulo...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-emerald-300" />
                  Ejecutar Peritaje Forense Completo
                </>
              )}
            </button>
          </div>
        </nav>

        {/* ALERTA DE ERROR DE VALIDACIÓN PERICIAL (SI SE SUBE UNA SELFIE O IMAGEN NO DOCUMENTAL) */}
        {validationError && (
          <div className="p-5 rounded-2xl bg-rose-50 border-2 border-rose-200 text-rose-900 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl shadow-rose-950/50">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-rose-100 border border-rose-300 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-6 h-6 text-rose-600 animate-bounce" />
              </div>
              <div>
                <h3 className="font-bold text-base text-rose-900 uppercase tracking-wide flex items-center gap-2">
                  {validationError.error_title || "Rechazo de Entrada Pericial"}
                  <span className="text-xs font-mono bg-rose-900 px-2 py-0.5 rounded text-rose-300 border border-rose-700">
                    Filtro Anti-Falsos Positivos
                  </span>
                </h3>
                <p className="text-sm text-rose-800 mt-1 leading-relaxed">
                  {validationError.message}
                </p>
                <p className="text-xs text-rose-700 mt-1">
                  💡 <strong>Principio de IA Responsable:</strong> Un sistema forense científico debe validar que el sensor capte un soporte documental antes de emitir un dictamen judicial.
                </p>
              </div>
            </div>
            <div className="flex gap-2 self-end md:self-center shrink-0">
              <button 
                onClick={startCamera}
                className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-all shadow-md"
              >
                Reintentar Cámara
              </button>
              <button 
                onClick={() => handleSelectSample('check_clean.png')}
                className="px-4 py-2 rounded-lg bg-[#EFECE6] hover:bg-slate-700 text-[#292524] font-semibold text-xs border border-[#D8D1C3] transition-all"
              >
                Probar Cheque Válido
              </button>
            </div>
          </div>
        )}

        {/* ALERTA DE RESULTADO RÁPIDO SI YA SE ANALIZÓ */}
        {report && (
          <div className={`p-4 rounded-xl border flex items-center justify-between ${
            report.fraud_points >= 40 
              ? 'bg-[#FDF2F2] border-[#F8D4D4] text-[#7A1F1D]' 
              : report.fraud_points >= 20 
                ? 'bg-[#FFFBEB] border-amber-300 text-[#854D0E]' 
                : 'bg-[#F2F7F2] border-[#D1E7D3] text-[#1E4620]'
          }`}>
            <div className="flex items-center gap-3">
              {report.fraud_points >= 40 ? (
                <XCircle className="w-7 h-7 text-rose-500" />
              ) : report.fraud_points >= 20 ? (
                <AlertTriangle className="w-7 h-7 text-amber-500" />
              ) : (
                <CheckCircle2 className="w-7 h-7 text-emerald-500" />
              )}
              <div>
                <div className="font-bold text-base">{report.global_verdict}</div>
                <div className="text-xs opacity-80">
                  Expediente: <span className="font-mono">{report.case_id}</span> | Riesgo Evidenciario: <strong>{report.fraud_points}%</strong> | Reglas Transgredidas: {report.rules_triggered_count}
                </div>
              </div>
            </div>
            <button 
              onClick={() => setActiveTab('report')}
              className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-[#F5F2EB] text-xs font-semibold border border-[#D8D1C3] text-[#1C1917] transition-all shadow-xs"
            >
              Ver Dictamen Judicial Completo →
            </button>
          </div>
        )}

        {/* PESTAÑA 1: INSPECCIÓN GENERAL & VISIÓN */}
        {activeTab === 'inspection' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                <h3 className="font-semibold text-[#1C1917] flex items-center gap-2 text-sm">
                  <Eye className="w-4 h-4 text-[#8B5E3C]" />
                  Visualizador de Evidencia Documental
                </h3>
                {analysisResults?.rectified_perspective && (
                  <span className="text-xs px-2 py-0.5 rounded bg-[#EFECE6] text-[#8B5E3C] border border-[#DDD7CC]">
                    Perspectiva Rectificada (Homografía 4-Puntos)
                  </span>
                )}
              </div>

              <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2 relative overflow-hidden">
                {currentImageBase64 ? (
                  <img 
                    src={analysisResults?.rectified_image_b64 || currentImageBase64} 
                    alt="Documento" 
                    className="max-h-[460px] w-auto object-contain rounded shadow-lg"
                  />
                ) : (
                  <div className="text-center text-[#A8A29E] text-sm">
                    <FileText className="w-12 h-12 mx-auto mb-2 opacity-40" />
                    Enfoca la cámara o selecciona una muestra forense arriba
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-6">
              {/* MÁSCARA BINARIA DE TINTA (OPENCV) */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4 text-[#8B5E3C]" />
                  Segmentación de Tinta (Otsu + Adaptativa)
                </h4>
                <div className="bg-[#F3EFE8] rounded-lg border border-[#DDD7CD] h-44 flex items-center justify-center p-2">
                  {analysisResults?.ink_mask_b64 ? (
                    <img src={analysisResults.ink_mask_b64} alt="Máscara de tinta" className="max-h-full object-contain filter invert" />
                  ) : (
                    <span className="text-xs text-slate-600">Presiona "Ejecutar Peritaje" para segmentar</span>
                  )}
                </div>
                <p className="text-xs text-[#78716C]">
                  Aísla los surcos del útil inscriptor eliminando el fondo y artefactos de iluminación.
                </p>
              </div>

              {/* FICHA TÉCNICA DEL CASO */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider">Metodología Pericial (Sílabo)</h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Preprocesamiento:</span>
                    <span className="text-[#292524] font-mono">OpenCV / Homografía / Otsu</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Clustering No Supervisado:</span>
                    <span className="text-[#292524] font-mono">K-Means + DBSCAN</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Reducción Dimensional:</span>
                    <span className="text-[#292524] font-mono">PCA (2 Componentes)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Clasificación Supervisada:</span>
                    <span className="text-[#292524] font-mono">Random Forest / XGBoost / SVM</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Deep Learning:</span>
                    <span className="text-[#292524] font-mono">Red Densa MLP (PyTorch)</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-[#78716C]">Búsqueda & Simbólica:</span>
                    <span className="text-[#292524] font-mono">Algoritmo A* + Reglas Pellat</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PESTAÑA 2: ESPECTROMETRÍA DE TINTAS (NO SUPERVISADO) */}
        {activeTab === 'inks' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                <div>
                  <h3 className="font-semibold text-[#1C1917] text-sm">Segmentación Espectral por Clústeres de Color</h3>
                  <p className="text-xs text-[#78716C]">K-Means agrupa los píxeles de tinta en el espacio LAB/HSV para revelar bolígrafos distintos</p>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-[#8B5E3C]"></span>
                    <span>Tinta Base (Cluster 0)</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                    <span>Tinta Adulterada (Cluster 1)</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2">
                {inks?.segmented_image_b64 ? (
                  <img src={inks.segmented_image_b64} alt="Segmentación de tintas" className="max-h-[440px] object-contain rounded" />
                ) : (
                  <div className="text-center text-[#A8A29E] text-sm">
                    Ejecuta el peritaje completo para visualizar los clústeres de tinta
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-6">
              {/* TARJETA SILHOUETTE SCORE */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider">Métrica de Silhouette Score</h4>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-bold font-mono text-[#8B5E3C]">
                    {inks ? inks.silhouette_score : '--'}
                  </span>
                  <span className="text-xs text-[#78716C]">Umbral Pericial: ≥ 0.380</span>
                </div>
                
                {/* Barra de progreso de Silhouette */}
                <div className="w-full bg-[#EFECE6] h-2.5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-700 ${
                      (inks?.silhouette_score || 0) >= 0.38 ? 'bg-rose-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.max(5, Math.min(100, ((inks?.silhouette_score || 0) + 1) * 50))}%` }}
                  />
                </div>

                <p className="text-xs text-[#44403C] leading-relaxed bg-[#FAF9F5]/60 p-3 rounded border border-[#E5E0D6]">
                  {inks ? inks.scientific_conclusion : "Evalúa cuantitativamente la separabilidad entre grupos de tinta."}
                </p>
              </div>

              {/* GRÁFICO PCA DE DISPERSIÓN 2D */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <div className="flex justify-between items-center">
                  <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider">Espacio PCA (2 Componentes)</h4>
                  <span className="text-xs font-mono text-[#78716C]">
                    Varianza: {inks ? (inks.pca_variance_explained.reduce((a,b)=>a+b,0)*100).toFixed(1) : 0}%
                  </span>
                </div>

                <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] h-52 relative p-2 flex items-center justify-center">
                  {inks?.pca_scatter_points && inks.pca_scatter_points.length > 0 ? (
                    <svg viewBox="-1.2 -1.2 2.4 2.4" className="w-full h-full">
                      {/* Ejes */}
                      <line x1="-1.2" y1="0" x2="1.2" y2="0" stroke="#334155" strokeWidth="0.02" />
                      <line x1="0" y1="-1.2" x2="0" y2="1.2" stroke="#334155" strokeWidth="0.02" />
                      {/* Puntos de dispersión */}
                      {inks.pca_scatter_points.map((pt, i) => (
                        <circle
                          key={i}
                          cx={pt.x}
                          cy={pt.y}
                          r={pt.is_outlier ? "0.05" : "0.035"}
                          fill={pt.is_outlier ? "#D97706" : pt.cluster === 0 ? "#3F3A36" : "#C2410C"}
                          opacity="0.8"
                        />
                      ))}
                    </svg>
                  ) : (
                    <span className="text-xs text-slate-600">Puntos PCA disponibles al analizar</span>
                  )}
                </div>
                <div className="flex justify-between text-[11px] text-[#78716C]">
                  <span>● Tinta 1 (Cian)</span>
                  <span>● Tinta 2 (Rosa)</span>
                  <span>● DBSCAN Outliers (Amarillo)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PESTAÑA 3: ADULTERACIÓN DE CIFRAS (SUPERVISADO) */}
        {activeTab === 'tampering' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                <div>
                  <h3 className="font-semibold text-[#1C1917] text-sm">Detección de Trazos Anómalos y Enmiendas en Cifras</h3>
                  <p className="text-xs text-[#78716C]">Identificación de adiciones morfológicas que alteran el valor nominal (ej. añadir un cero o alterar dígitos)</p>
                </div>
                <span className="text-xs px-2.5 py-1 rounded bg-[#EFECE6] text-[#8B5E3C] font-mono border border-[#D8D1C3]">
                  Clasificador: {tampering?.best_model_used || "Ensemble"}
                </span>
              </div>

              <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2">
                {tampering?.annotated_image_b64 ? (
                  <img src={tampering.annotated_image_b64} alt="Adulteraciones marcadas" className="max-h-[440px] object-contain rounded" />
                ) : (
                  <div className="text-center text-[#A8A29E] text-sm">
                    Ejecuta el peritaje completo para detectar enmiendas en cifras
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-6">
              {/* TABLA COMPARATIVA DE MODELOS SUPERVISADOS (SÍLABO) */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-[#8B5E3C]" />
                  Comparativa de Modelos Candidatos (Sílabo)
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-[#E5E0D6] text-[#78716C]">
                        <th className="pb-2 font-medium">Modelo</th>
                        <th className="pb-2 font-medium">Accuracy</th>
                        <th className="pb-2 font-medium">F1-Score</th>
                        <th className="pb-2 font-medium">ROC-AUC</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {benchmarkData?.models_evaluated ? (
                        Object.entries(benchmarkData.models_evaluated).map(([mName, mMetrics]) => (
                          <tr key={mName} className={mName === benchmarkData.best_model ? "bg-[#EFECE6]/30 text-[#8B5E3C] font-semibold" : "text-[#44403C]"}>
                            <td className="py-2 pr-2">{mName}</td>
                            <td className="py-2 font-mono">{(mMetrics.accuracy * 100).toFixed(1)}%</td>
                            <td className="py-2 font-mono">{(mMetrics.f1_score * 100).toFixed(1)}%</td>
                            <td className="py-2 font-mono">{(mMetrics.roc_auc).toFixed(3)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr><td colSpan="4" className="py-4 text-center text-slate-600">Cargando métricas...</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* MATRIZ DE CONFUSIÓN DEL MEJOR MODELO */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider">Matriz de Confusión (Test Set)</h4>
                {benchmarkData?.models_evaluated?.[benchmarkData.best_model]?.confusion_matrix ? (
                  <div className="grid grid-cols-2 gap-2 text-center text-xs font-mono">
                    <div className="bg-[#EFECE6]/40 border border-[#DDD7CC]/60 p-2.5 rounded">
                      <div className="text-[#78716C] text-[10px]">Verdaderos Negativos (TN)</div>
                      <div className="text-lg font-bold text-[#8B5E3C]">
                        {benchmarkData.models_evaluated[benchmarkData.best_model].confusion_matrix[0][0]}
                      </div>
                    </div>
                    <div className="bg-rose-50 border border-rose-200 p-2.5 rounded">
                      <div className="text-[#78716C] text-[10px]">Falsos Positivos (FP)</div>
                      <div className="text-lg font-bold text-rose-700">
                        {benchmarkData.models_evaluated[benchmarkData.best_model].confusion_matrix[0][1]}
                      </div>
                    </div>
                    <div className="bg-amber-50 border border-amber-200 p-2.5 rounded">
                      <div className="text-[#78716C] text-[10px]">Falsos Negativos (FN)</div>
                      <div className="text-lg font-bold text-amber-700">
                        {benchmarkData.models_evaluated[benchmarkData.best_model].confusion_matrix[1][0]}
                      </div>
                    </div>
                    <div className="bg-[#EFECE6]/50 border border-[#DDD7CC]/60 p-2.5 rounded">
                      <div className="text-[#78716C] text-[10px]">Verdaderos Positivos (TP)</div>
                      <div className="text-lg font-bold text-[#8B5E3C]">
                        {benchmarkData.models_evaluated[benchmarkData.best_model].confusion_matrix[1][1]}
                      </div>
                    </div>
                  </div>
                ) : (
                  <span className="text-xs text-slate-600">Matriz disponible al conectar backend</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* PESTAÑA 4: COTEJO DE FIRMA & DINÁMICA MOTORA (DEEP LEARNING) */}
        {activeTab === 'signature' && (
          <div className="flex flex-col gap-5">
            {/* SELECTOR DE MODO DE FIRMA: DOCUMENTO vs COTEJO DUAL EN LA MISMA HOJA */}
            <div className="flex items-center gap-2 bg-[#EFECE6] p-1 rounded-xl w-fit border border-[#E2DDD3]">
              <button
                onClick={() => setSignatureTabMode('document')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  signatureTabMode === 'document'
                    ? 'bg-white text-[#1C1917] shadow-sm'
                    : 'text-[#78716C] hover:text-[#1C1917]'
                }`}
              >
                Modo Documento Completo
              </button>
              <button
                onClick={() => setSignatureTabMode('dual')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  signatureTabMode === 'dual'
                    ? 'bg-white text-[#1C1917] shadow-sm'
                    : 'text-[#78716C] hover:text-[#1C1917]'
                }`}
              >
                🔬 Modo Cotejo Dual (2 Firmas en la Misma Hoja)
              </button>
            </div>

            {/* MODO COTEJO DUAL */}
            {signatureTabMode === 'dual' && (
              <div className="flex flex-col gap-6">
                <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 shadow-[0_1px_3px_rgba(0,0,0,0.03)] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-[#1C1917] text-sm flex items-center gap-2">
                      Cotejo Grafotécnico Directo (Firma Indubitada vs. Firma Dubitada)
                    </h3>
                    <p className="text-xs text-[#78716C] mt-1">
                      Coloca en una <strong>misma hoja</strong> tu firma original a la <strong>izquierda</strong> y la imitación/sospechosa a la <strong>derecha</strong>.
                    </p>
                  </div>
                  <button
                    onClick={runDualComparison}
                    disabled={isComparingDual || !currentImageBase64}
                    className="px-5 py-2.5 rounded-lg bg-[#1C1917] hover:bg-[#38332F] text-[#FAF8F5] text-xs font-semibold shadow-sm transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    {isComparingDual ? "Analizando Dinámica Dual..." : "Ejecutar Cotejo Grafotécnico (Firma vs Firma)"}
                  </button>
                </div>

                {dualComparisonResults ? (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* VISUALIZACIÓN ANOTADA CON RECUADROS */}
                    <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                      <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                        <span className="text-xs font-semibold text-[#1C1917]">Segmentación y Delimitación Pericial de Firmas</span>
                        <span className={`text-xs px-2.5 py-0.5 rounded font-bold ${
                          dualComparisonResults.is_forgery 
                            ? 'bg-rose-50 text-rose-800 border border-rose-200' 
                            : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                        }`}>
                          {dualComparisonResults.verdict}
                        </span>
                      </div>
                      <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2">
                        <img 
                          src={dualComparisonResults.annotated_image_b64 || currentImageBase64} 
                          alt="Cotejo Dual Anotado" 
                          className="max-h-[460px] w-auto object-contain rounded"
                        />
                      </div>
                    </div>

                    {/* TARJETA COMPARATIVA LADO A LADO */}
                    <div className="flex flex-col gap-5">
                      <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                        <h4 className="text-xs font-semibold text-[#44403C] uppercase tracking-wider">Cotejo Biomecánico Diferencial</h4>
                        
                        {/* Similitud Morfológica */}
                        <div className="bg-[#F8F6F0] p-3 rounded-lg border border-[#E5E0D6]">
                          <div className="text-[11px] text-[#78716C]">Similitud Geométrica de Forma:</div>
                          <div className="text-xl font-bold font-mono text-[#1C1917] mt-0.5">
                            {(dualComparisonResults.morphological_similarity * 100).toFixed(1)}%
                          </div>
                          <div className="text-[10px] text-[#78716C] mt-1">Similitud visual aparente de trazos</div>
                        </div>

                        {/* Comparación Firma 1 vs Firma 2 */}
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {/* Izquierda */}
                          <div className="p-3 rounded-lg bg-emerald-50/70 border border-emerald-200">
                            <div className="font-bold text-emerald-900 text-[11px]">Firma Izquierda</div>
                            <div className="text-[10px] text-emerald-700 font-semibold mb-2">Patrón Original</div>
                            <div className="space-y-1 text-[11px] text-emerald-950">
                              <div>Temblores: <strong>{dualComparisonResults.left_signature?.tremor_score}</strong>/100</div>
                              <div>Velocidad: <strong>{dualComparisonResults.left_signature?.kinematic_speed}</strong>/100</div>
                              <div>Presión: <strong>{dualComparisonResults.left_signature?.motor_pressure}</strong>/100</div>
                            </div>
                          </div>

                          {/* Derecha */}
                          <div className={`p-3 rounded-lg border ${
                            dualComparisonResults.is_forgery 
                              ? 'bg-rose-50/70 border-rose-200 text-rose-950' 
                              : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                          }`}>
                            <div className="font-bold text-[11px]">Firma Derecha</div>
                            <div className="text-[10px] font-semibold mb-2">
                              {dualComparisonResults.is_forgery ? 'Imitación Sospechosa' : 'Genuina'}
                            </div>
                            <div className="space-y-1 text-[11px]">
                              <div>Temblores: <strong>{dualComparisonResults.right_signature?.tremor_score}</strong>/100</div>
                              <div>Velocidad: <strong>{dualComparisonResults.right_signature?.kinematic_speed}</strong>/100</div>
                              <div>Presión: <strong>{dualComparisonResults.right_signature?.motor_pressure}</strong>/100</div>
                            </div>
                          </div>
                        </div>

                        {/* Fundamento Causal */}
                        <div className="p-3 bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] text-xs leading-relaxed text-[#44403C]">
                          <strong className="text-[#1C1917] block mb-1">Dictamen de Solange Pellat:</strong>
                          {dualComparisonResults.scientific_conclusion}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white border border-[#E5E0D6] rounded-xl p-12 text-center text-[#78716C] shadow-sm">
                    <p className="text-sm font-medium text-[#1C1917]">Cotejo Grafotécnico Dual Listo</p>
                    <p className="text-xs text-[#78716C] mt-1 max-w-md mx-auto">
                      Enfoca con la cámara o sube una foto donde hayas escrito dos firmas en la misma hoja (tu firma a la izquierda y la imitación a la derecha) y pulsa el botón de arriba.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* MODO DOCUMENTO COMPLETO (HABITUAL) */}
            {signatureTabMode === 'document' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-5 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                <div>
                  <h3 className="font-semibold text-[#1C1917] text-sm">Verificación de Firma y Diagnóstico Neuromotor</h3>
                  <p className="text-xs text-[#78716C]">Red Neuronal Densa (PyTorch MLP) + Regresión Ridge para presión y velocidad del trazo</p>
                </div>
                {signature && (
                  <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
                    signature.is_genuine 
                      ? 'bg-[#EFECE6] text-[#8B5E3C] border border-[#DDD7CC]' 
                      : 'bg-rose-950 text-rose-400 border border-rose-800'
                  }`}>
                    {signature.verdict}
                  </span>
                )}
              </div>

              {/* 3 MEDIDORES CINEMÁTICOS */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#FAF9F5] p-4 rounded-xl border border-[#E5E0D6] flex flex-col gap-2">
                  <span className="text-xs text-[#78716C] uppercase font-semibold">Presión Motora Estimada</span>
                  <div className="text-2xl font-bold font-mono text-[#8B5E3C]">
                    {signature ? `${signature.motor_pressure_index}` : '--'}<span className="text-xs text-[#A8A29E]">/100</span>
                  </div>
                  <div className="w-full bg-[#EFECE6] h-2 rounded-full overflow-hidden">
                    <div className="bg-[#8B5E3C] h-full" style={{ width: `${signature?.motor_pressure_index || 0}%` }} />
                  </div>
                  <span className="text-[11px] text-[#A8A29E]">Regresión Ridge sobre gradiente de borde</span>
                </div>

                <div className="bg-[#FAF9F5] p-4 rounded-xl border border-[#E5E0D6] flex flex-col gap-2">
                  <span className="text-xs text-[#78716C] uppercase font-semibold">Velocidad Cinemática</span>
                  <div className="text-2xl font-bold font-mono text-[#8B5E3C]">
                    {signature ? `${signature.kinematic_speed_index}` : '--'}<span className="text-xs text-[#A8A29E]">/100</span>
                  </div>
                  <div className="w-full bg-[#EFECE6] h-2 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full" style={{ width: `${signature?.kinematic_speed_index || 0}%` }} />
                  </div>
                  <span className="text-[11px] text-[#A8A29E]">Ley de Pellat 1: Fluidez subconsciente</span>
                </div>

                <div className="bg-[#FAF9F5] p-4 rounded-xl border border-[#E5E0D6] flex flex-col gap-2">
                  <span className="text-xs text-[#78716C] uppercase font-semibold">Ataxia / Micro-Temblores</span>
                  <div className="text-2xl font-bold font-mono text-rose-400">
                    {signature ? `${signature.tremor_score}` : '--'}<span className="text-xs text-[#A8A29E]">/100</span>
                  </div>
                  <div className="w-full bg-[#EFECE6] h-2 rounded-full overflow-hidden">
                    <div className="bg-rose-500 h-full" style={{ width: `${signature?.tremor_score || 0}%` }} />
                  </div>
                  <span className="text-[11px] text-[#A8A29E]">Ley de Pellat 2: Esfuerzo inhibitorio</span>
                </div>
              </div>

              {/* EXPLICACIÓN GRAFOTÉCNICA */}
              <div className="bg-[#FAF9F5] p-4 rounded-xl border border-[#E5E0D6]">
                <h4 className="text-xs font-semibold text-[#44403C] uppercase tracking-wider mb-2">Dictamen Pericial de Autenticidad</h4>
                <p className="text-xs text-[#44403C] leading-relaxed">
                  {signature ? signature.explanation : "El módulo clasifica si la firma exhibe los automatismos neuromotores naturales del autor o el titubeo lento de una falsificación."}
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-6">
              {/* CURVA DE APRENDIZAJE DEEP LEARNING (PÉRDIDA / LOSS) */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <div className="flex justify-between items-center">
                  <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider">Entrenamiento PyTorch MLP</h4>
                  <span className="text-xs font-mono text-[#78716C]">BCELoss / Adam</span>
                </div>
                <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] h-48 relative p-3 flex items-end justify-between gap-1">
                  {signature?.training_epochs_loss && signature.training_epochs_loss.length > 0 ? (
                    signature.training_epochs_loss.map((item, idx) => (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-1 group">
                        <div 
                          className="w-full bg-gradient-to-t from-emerald-600 to-teal-400 rounded-t transition-all group-hover:bg-[#8B5E3C]"
                          style={{ height: `${Math.max(10, Math.min(100, item.loss * 160))}%` }}
                        />
                        <span className="text-[9px] text-[#A8A29E] font-mono">{item.epoch}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-600 w-full text-center">Curva de pérdida al ejecutar</span>
                  )}
                </div>
                <div className="flex justify-between text-[11px] text-[#78716C]">
                  <span>Época 1 (Pérdida Inicial)</span>
                  <span>Época 25 (Convergencia Óptima)</span>
                </div>
              </div>
            </div>
          </div>
            )}
          </div>
        )}

        {/* PESTAÑA 5: CRUCE CRONOLÓGICO DE TRAZOS (ALGORITMO A*) */}
        {activeTab === 'chronology' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-3">
                <div>
                  <h3 className="font-semibold text-[#1C1917] text-sm">Inspección de Continuidad en Intersecciones (Algoritmo A*)</h3>
                  <p className="text-xs text-[#78716C]">Búsqueda de trayectoria óptima de flujo de tinta para resolver el fraude de "Firma en Blanco"</p>
                </div>
                {chronology && (
                  <span className={`text-xs px-3 py-1 rounded-full font-bold ${
                    chronology.blank_signature_fraud 
                      ? 'bg-rose-950 text-rose-400 border border-rose-800' 
                      : 'bg-[#EFECE6] text-[#8B5E3C] border border-[#DDD7CC]'
                  }`}>
                    {chronology.blank_signature_fraud ? 'FIRMA EN BLANCO DETECTADA' : 'SECUENCIA NORMAL'}
                  </span>
                )}
              </div>

              <div className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2">
                {chronology?.visualization_b64 ? (
                  <img src={chronology.visualization_b64} alt="Cruce A*" className="max-h-[440px] object-contain rounded" />
                ) : (
                  <div className="text-center text-[#A8A29E] text-sm">
                    Ejecuta el peritaje completo para analizar la intersección con el algoritmo A*
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-6">
              {/* MÉTRICAS DEL ALGORITMO A* */}
              <div className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
                <h4 className="font-semibold text-[#44403C] text-xs uppercase tracking-wider flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-[#8B5E3C]" />
                  Métricas de Búsqueda Informada (A*)
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Nodos Explorados (Estados):</span>
                    <span className="text-[#292524] font-mono font-bold">{chronology ? chronology.nodes_explored_a_star : '--'}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Costo Trazo Firma:</span>
                    <span className="text-[#8B5E3C] font-mono font-bold">{chronology ? chronology.horizontal_path_cost : '--'}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-[#E5E0D6]">
                    <span className="text-[#78716C]">Costo Trazo Texto:</span>
                    <span className="text-orange-400 font-mono font-bold">{chronology ? chronology.vertical_path_cost : '--'}</span>
                  </div>
                  <div className="flex justify-between py-1.5">
                    <span className="text-[#78716C]">Trazo Superior Físico:</span>
                    <span className="text-[#8B5E3C] font-bold">{chronology ? chronology.top_stroke : '--'}</span>
                  </div>
                </div>

                <div className="bg-[#FAF9F5] p-3 rounded border border-[#E5E0D6] text-xs text-[#44403C] mt-2">
                  <strong>Principio Físico:</strong> En microfotografía pericial, el trazo que se estampó <em>después</em> (encima) presenta continuidad especular ininterrumpida sin fisuras en los límites de intersección.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PESTAÑA 6: DICTAMEN JUDICIAL OFICIAL (SISTEMA EXPERTO) */}
        {activeTab === 'report' && (
          <div className="max-w-4xl mx-auto w-full bg-white border border-[#E5E0D6] rounded-2xl p-8 flex flex-col gap-6 shadow-sm">
            <div className="flex items-center justify-between border-b border-[#E5E0D6] pb-5">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-[#EFECE6] border border-[#D8D1C3] flex items-center justify-center">
                  <Scale className="w-6 h-6 text-[#8B5E3C]" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#1C1917]">Dictamen Pericial Oficial</h2>
                  <p className="text-xs text-[#78716C]">Acta Judicial con Cadena de Custodia Criptográfica</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  onClick={() => window.print()}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EFECE6] hover:bg-slate-700 text-[#292524] text-xs font-semibold border border-[#D8D1C3]"
                >
                  <Download className="w-4 h-4" />
                  Imprimir / Exportar PDF
                </button>
              </div>
            </div>

            {report ? (
              <div className="space-y-6 text-sm text-[#44403C]">
                {/* TARJETA DE VEREDICTO */}
                <div className={`p-5 rounded-xl border ${
                  report.fraud_points >= 40 
                    ? 'bg-rose-50 border-rose-200 text-rose-900' 
                    : report.fraud_points >= 20 
                      ? 'bg-amber-50 border-amber-200 text-amber-900' 
                      : 'bg-emerald-50 border-emerald-200 text-emerald-900'
                }`}>
                  <div className="text-xs uppercase font-bold tracking-wider opacity-75">Conclusión del Tribunal Pericial:</div>
                  <div className="text-2xl font-bold mt-1">{report.global_verdict}</div>
                  <div className="text-xs mt-2 opacity-90">
                    Hash SHA-256 de Evidencia: <code className="font-mono bg-white px-2 py-0.5 rounded border border-stone-200 text-stone-800">{report.doc_hash}</code>
                  </div>
                </div>

                {/* REGLAS TRANSGREDIDAS */}
                <div>
                  <h4 className="font-semibold text-[#1C1917] text-xs uppercase tracking-wider mb-3">Reglas Forenses y Fundamento Causal:</h4>
                  <div className="space-y-2">
                    {report.rules_triggered.map((rule, idx) => (
                      <div key={idx} className="p-3 bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-[#8B5E3C] text-xs font-bold">{rule.code} - {rule.name}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-rose-50 text-rose-800 border border-rose-200 font-bold">{rule.severity}</span>
                        </div>
                        <p className="text-xs text-[#44403C]">{rule.justification}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* TEXTO COMPLETO DEL DICTAMEN */}
                <div>
                  <h4 className="font-semibold text-[#1C1917] text-xs uppercase tracking-wider mb-2">Transcripción del Acta Judicial:</h4>
                  <pre className="p-4 bg-[#FAF9F5] rounded-xl border border-[#E5E0D6] text-xs font-mono text-[#44403C] whitespace-pre-wrap leading-relaxed overflow-x-auto max-h-96">
                    {report.official_report_markdown}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-[#A8A29E] text-sm">
                Ejecuta el peritaje completo para generar el Dictamen Pericial Judicial.
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}

