with open('Frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Polishing light beige aesthetic
text = text.replace('className="max-w-4xl mx-auto w-full bg-[#F5F2EB] border border-[#E5E0D6] rounded-2xl p-8 flex flex-col gap-6 shadow-2xl"',
                    'className="max-w-4xl mx-auto w-full bg-white border border-[#E5E0D6] rounded-2xl p-8 flex flex-col gap-6 shadow-sm"')

text = text.replace('<h2 className="text-lg font-bold text-white">Dictamen Pericial Oficial</h2>',
                    '<h2 className="text-lg font-bold text-[#1C1917]">Dictamen Pericial Oficial</h2>')

text = text.replace('<h4 className="font-semibold text-white text-xs uppercase tracking-wider mb-3">Reglas',
                    '<h4 className="font-semibold text-[#1C1917] text-xs uppercase tracking-wider mb-3">Reglas')

text = text.replace('<h4 className="font-semibold text-white text-xs uppercase tracking-wider mb-2">Transc',
                    '<h4 className="font-semibold text-[#1C1917] text-xs uppercase tracking-wider mb-2">Transc')

text = text.replace('className="px-3.5 py-1.5 rounded-lg bg-[#F5F2EB]/80 hover:bg-[#F5F2EB] text-xs font-semibold border border-[#D8D1C3] text-white transition-all"',
                    'className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-[#F5F2EB] text-xs font-semibold border border-[#D8D1C3] text-[#1C1917] transition-all shadow-xs"')

# Confusion matrix soft badges
text = text.replace('bg-rose-950/40 border border-rose-800/60 p-2.5 rounded', 'bg-rose-50 border border-rose-200 p-2.5 rounded')
text = text.replace('text-lg font-bold text-rose-400', 'text-lg font-bold text-rose-700')
text = text.replace('bg-amber-950/40 border border-amber-800/60 p-2.5 rounded', 'bg-amber-50 border border-amber-200 p-2.5 rounded')
text = text.replace('text-lg font-bold text-amber-400', 'text-lg font-bold text-amber-700')

# Report alert banner
target_banner_old = "report.fraud_points >= 40 \n                    ? 'bg-rose-950/30 border-rose-800 text-rose-200' \n                    : report.fraud_points >= 20 \n                      ? 'bg-amber-950/30 border-amber-800 text-amber-200' \n                      : 'bg-[#EFECE6]/30 border-[#DDD7CC] text-emerald-200'"
target_banner_new = "report.fraud_points >= 40 \n                    ? 'bg-rose-50 border-rose-200 text-rose-900' \n                    : report.fraud_points >= 20 \n                      ? 'bg-amber-50 border-amber-200 text-amber-900' \n                      : 'bg-emerald-50 border-emerald-200 text-emerald-900'"
text = text.replace(target_banner_old, target_banner_new)

text = text.replace('code className="font-mono bg-black/40 px-2 py-0.5 rounded"',
                    'code className="font-mono bg-white px-2 py-0.5 rounded border border-stone-200 text-stone-800"')

text = text.replace('text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800',
                    'text-[10px] px-2 py-0.5 rounded bg-rose-50 text-rose-800 border border-rose-200')

# Signature card background
text = text.replace('bg-[#F5F2EB]/60 border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-5',
                    'bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-5 shadow-[0_1px_3px_rgba(0,0,0,0.03)]')

# Validation error card in light mode
text = text.replace('bg-rose-950/40 border-2 border-rose-500/80 text-rose-100',
                    'bg-rose-50 border-2 border-rose-200 text-rose-900')
text = text.replace('bg-rose-900/60 border border-rose-700', 'bg-rose-100 border border-rose-300')
text = text.replace('text-rose-400 animate-bounce', 'text-rose-600 animate-bounce')
text = text.replace('text-rose-200 uppercase tracking-wide', 'text-rose-900 uppercase tracking-wide')
text = text.replace('text-rose-200/90 mt-1', 'text-rose-800 mt-1')
text = text.replace('text-rose-300/70 mt-1', 'text-rose-700 mt-1')

with open('Frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print('App.jsx polished successfully!')
