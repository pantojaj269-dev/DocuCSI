with open('Frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add states after line 'const [validationError, setValidationError] = useState(null);'
target_state = "const [validationError, setValidationError] = useState(null);"
replacement_state = """const [validationError, setValidationError] = useState(null);

  const [signatureTabMode, setSignatureTabMode] = useState('document'); // 'document' | 'dual'
  const [dualComparisonResults, setDualComparisonResults] = useState(null);
  const [isComparingDual, setIsComparingDual] = useState(false);"""

code = code.replace(target_state, replacement_state, 1)

# 2. Add runDualComparison function after handleSelectSample or similar
target_func = "const handleSelectSample = (sampleId) => {"
replacement_func = """const runDualComparison = async () => {
    if (!currentImageBase64) return;
    setIsComparingDual(true);
    try {
      const res = await fetch('/api/signatures/compare_dual', {
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

  const handleSelectSample = (sampleId) => {"""

code = code.replace(target_func, replacement_func, 1)

# 3. In Tab 4 (activeTab === 'signature'), add mode toggle buttons and dual mode UI
target_tab4 = "{/* PESTAÑA 4: COTEJO DE FIRMA & DINÁMICA MOTORA (DEEP LEARNING) */}\n        {activeTab === 'signature' && ("
replacement_tab4 = """{/* PESTAÑA 4: COTEJO DE FIRMA & DINÁMICA MOTORA (DEEP LEARNING) */}
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
            {signatureTabMode === 'document' && ("""

code = code.replace(target_tab4, replacement_tab4, 1)

# Close the wrapper div at the end of Tab 4 before Tab 5
target_end_tab4 = "            </div>\n          </div>\n        )}\n\n        {/* PESTAÑA 5: CRUCE CRONOLÓGICO DE TRAZOS"
replacement_end_tab4 = "            </div>\n          </div>\n            )}\n          </div>\n        )}\n\n        {/* PESTAÑA 5: CRUCE CRONOLÓGICO DE TRAZOS"

code = code.replace(target_end_tab4, replacement_end_tab4, 1)

with open('Frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('Dual mode successfully integrated into App.jsx!')
