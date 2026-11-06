import re

with open('Frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Background & Root container
text = text.replace(
    'className="min-h-screen bg-[#060c08] text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-slate-950"',
    'className="min-h-screen bg-[#F8F6F0] text-[#292524] flex flex-col selection:bg-[#E5DFD3] selection:text-[#1C1917]"'
)

# 2. Header
text = text.replace(
    'className="border-b border-slate-800 bg-slate-900/70 backdrop-blur-md px-6 py-4 sticky top-0 z-50 flex items-center justify-between"',
    'className="border-b border-[#E5E0D6] bg-white/85 backdrop-blur-md px-6 py-4 sticky top-0 z-50 flex items-center justify-between shadow-[0_1px_3px_rgba(0,0,0,0.02)]"'
)
text = text.replace(
    'className="w-10 h-10 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/25"',
    'className="w-10 h-10 rounded-lg bg-[#292524] flex items-center justify-center shadow-sm"'
)
text = text.replace(
    'Docu<span className="text-emerald-400">CSI</span>',
    'Docu<span className="text-[#8B5E3C]">CSI</span>'
)
text = text.replace(
    'className="font-mono text-xl font-bold tracking-wider text-white"',
    'className="font-mono text-xl font-bold tracking-wider text-[#1C1917]"'
)
text = text.replace(
    'className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80"',
    'className="text-xs font-semibold px-2 py-0.5 rounded bg-[#EFECE6] text-[#78350F] border border-[#DDD7CC]"'
)
text = text.replace('Motor IA: <strong className="text-slate-200">', 'Motor IA: <strong className="text-[#1C1917]">')
text = text.replace('Cadena de Custodia: <strong className="text-slate-200">', 'Cadena de Custodia: <strong className="text-[#1C1917]">')

# 3. Capture & Sample Bar
text = text.replace(
    'className="bg-slate-900 border-b border-slate-800 px-6 py-3"',
    'className="bg-[#EFECE6] border-b border-[#E2DDD3] px-6 py-2.5"'
)
text = text.replace(
    ": 'bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold shadow-lg shadow-emerald-600/30'",
    ": 'bg-[#292524] hover:bg-[#3F3A36] text-[#FAF8F5] font-medium shadow-sm'"
)
text = text.replace(
    'className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"',
    'className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium bg-white hover:bg-[#F5F2EC] text-[#292524] border border-[#DDD7CD] shadow-sm transition-all"'
)
text = text.replace(
    'className="rounded bg-slate-800 border-slate-700 text-emerald-400 focus:ring-0"',
    'className="rounded bg-white border-[#DDD7CD] text-[#8B5E3C] focus:ring-0"'
)
text = text.replace(
    "? 'bg-emerald-400 text-slate-950 font-bold shadow-md shadow-emerald-400/25'",
    "? 'bg-[#292524] text-[#FAF8F5] font-semibold shadow-sm'"
)
text = text.replace(
    ": 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'",
    ": 'bg-white hover:bg-[#F5F2EB] text-[#57534E] border border-[#DDD7CD]'"
)

# 4. Camera Modal
text = text.replace(
    'className="bg-slate-950 border-b border-emerald-900/50 p-6 flex flex-col items-center"',
    'className="bg-[#EAE5DB] border-b border-[#D8D1C3] p-6 flex flex-col items-center"'
)
text = text.replace(
    'className="relative rounded-xl overflow-hidden border-2 border-emerald-500 shadow-2xl shadow-emerald-500/20 max-w-2xl w-full"',
    'className="relative rounded-xl overflow-hidden border-2 border-[#8B5E3C] shadow-xl max-w-2xl w-full"'
)
text = text.replace(
    'border border-emerald-400/40', 'border border-[#8B5E3C]/40'
)
text = text.replace(
    'border border-dashed border-emerald-400/60', 'border border-dashed border-[#8B5E3C]/60'
)
text = text.replace(
    'className="text-xs font-mono text-teal-300 bg-slate-950/80 px-2 py-1 rounded"',
    'className="text-xs font-mono text-[#FAF8F5] bg-[#1C1917]/80 px-2 py-1 rounded"'
)

# 5. Navigation Tabs
text = text.replace(
    'className="flex flex-wrap gap-2 border-b border-slate-800 pb-2"',
    'className="flex flex-wrap gap-2 border-b border-[#E2DDD3] pb-2"'
)
text = text.replace(
    "? 'bg-slate-800 text-emerald-400 border-b-2 border-emerald-400 shadow-md'",
    "? 'bg-white text-[#1C1917] border-b-2 border-[#1C1917] shadow-sm font-semibold'"
)
text = text.replace(
    ": 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'",
    ": 'text-[#78716C] hover:text-[#1C1917] hover:bg-[#EFECE6]'"
)
text = text.replace(
    "${isActive ? 'text-emerald-400' : 'text-slate-500'}",
    "${isActive ? 'text-[#8B5E3C]' : 'text-[#A8A29E]'}"
)

# 6. Run Analysis Button
text = text.replace(
    'className="flex items-center gap-2 px-5 py-2 rounded-lg font-bold text-sm bg-gradient-to-r from-emerald-600 to-emerald-600 hover:from-emerald-500 hover:to-emerald-500 text-white shadow-lg shadow-emerald-500/20 disabled:opacity-50 transition-all"',
    'className="flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm bg-[#1C1917] hover:bg-[#38332F] text-[#FAF8F5] shadow-sm disabled:opacity-50 transition-all cursor-pointer"'
)
text = text.replace(
    'className="flex items-center gap-2 px-5 py-2 rounded-lg font-bold text-sm bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/30 transition-all cursor-pointer"',
    'className="flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm bg-[#1C1917] hover:bg-[#38332F] text-[#FAF8F5] shadow-sm disabled:opacity-50 transition-all cursor-pointer"'
)

# 7. Quick report summary alert
text = text.replace(
    ": report.fraud_points >= 20 \n                ? 'bg-amber-950/40 border-amber-800/80 text-amber-200' \n                : 'bg-emerald-950/40 border-emerald-800/80 text-emerald-200'",
    ": report.fraud_points >= 20 \n                ? 'bg-[#FFFBEB] border-amber-300 text-[#854D0E]' \n                : 'bg-[#F2F7F2] border-[#D1E7D3] text-[#1E4620]'"
)
text = text.replace(
    "? 'bg-rose-950/40 border-rose-800/80 text-rose-200'",
    "? 'bg-[#FDF2F2] border-[#F8D4D4] text-[#7A1F1D]'"
)

# 8. Cards & Containers throughout tabs
text = text.replace(
    'className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-4"',
    'className="lg:col-span-2 bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"'
)
text = text.replace(
    'className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-4"',
    'className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"'
)
text = text.replace(
    'className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-3"',
    'className="bg-white border border-[#E5E0D6] rounded-xl p-5 flex flex-col gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"'
)
text = text.replace(
    'className="bg-slate-900/60 border border-slate-800 rounded-xl p-5"',
    'className="bg-white border border-[#E5E0D6] rounded-xl p-5 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"'
)
text = text.replace(
    'className="bg-slate-900/60 border border-slate-800 rounded-xl p-6"',
    'className="bg-white border border-[#E5E0D6] rounded-xl p-6 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"'
)

# Inner visualizers
text = text.replace(
    'className="bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-center min-h-[380px] p-2 relative overflow-hidden"',
    'className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2 relative overflow-hidden"'
)
text = text.replace(
    'className="bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-center min-h-[380px] p-2"',
    'className="bg-[#FAF9F5] rounded-lg border border-[#E5E0D6] flex items-center justify-center min-h-[380px] p-2"'
)
text = text.replace(
    'className="bg-black rounded-lg border border-slate-800 h-44 flex items-center justify-center p-2"',
    'className="bg-[#F3EFE8] rounded-lg border border-[#DDD7CD] h-44 flex items-center justify-center p-2"'
)

# Headings in cards
text = text.replace('className="font-semibold text-slate-200', 'className="font-semibold text-[#1C1917]')
text = text.replace('className="font-semibold text-slate-300', 'className="font-semibold text-[#44403C]')
text = text.replace('text-slate-400', 'text-[#78716C]')
text = text.replace('text-slate-500', 'text-[#A8A29E]')
text = text.replace('text-slate-300', 'text-[#44403C]')
text = text.replace('text-slate-200', 'text-[#292524]')
text = text.replace('border-slate-800', 'border-[#E5E0D6]')
text = text.replace('border-slate-700', 'border-[#D8D1C3]')
text = text.replace('bg-slate-950', 'bg-[#FAF9F5]')
text = text.replace('bg-slate-900', 'bg-[#F5F2EB]')
text = text.replace('bg-slate-800', 'bg-[#EFECE6]')

# Emerald highlights to warm bronze/terracotta
text = text.replace('text-emerald-400', 'text-[#8B5E3C]')
text = text.replace('text-teal-300', 'text-[#8B5E3C]')
text = text.replace('bg-emerald-400', 'bg-[#8B5E3C]')
text = text.replace('bg-emerald-950', 'bg-[#EFECE6]')
text = text.replace('border-emerald-800', 'border-[#DDD7CC]')

# PCA scatter plot dots & Recharts
text = text.replace('#10b981', '#3F3A36') # cluster 0: espresso
text = text.replace('#f43f5e', '#C2410C') # cluster 1: terracotta
text = text.replace('#facc15', '#D97706') # outliers: amber

with open('Frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print('Transformation to Warm Beige Minimalist theme completed!')
